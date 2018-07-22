#include <boost/interprocess/streams/bufferstream.hpp>
#include <gateway.h>
#include <iomanip>
#include <iostream>
#include <packets.h>
#include <utils.h>

using boost::asio::ip::tcp;

void session::start() { do_read(); }

void session::send(message msg) {
  post(socket_.get_executor(), [=] {
    send_queue_.push(msg);
    do_write();
  });
}

void session::do_read() {
  auto self(shared_from_this());
  socket_.async_read_some(
      boost::asio::buffer(data_, max_length),
      [this, self](boost::system::error_code ec, std::size_t length) {
        std::cout << "RECV " << socket_.remote_endpoint() << "\t"
                  << print_hex(data_, length) << std::endl;
        if (!ec) {
          process(length);
          do_read();
        } else {
          // TODO handle disconnect
          gateway_->remove_client(this->addr_);
        }
      });
}

void session::do_write() {
  if (send_queue_.empty()) {
    return;
  }

  std::ostringstream out;
  auto msg = send_queue_.front();
  send_queue_.pop();
  msg.write(out);
  auto str = out.str();
  std::cout << "SEND " << socket_.remote_endpoint() << "\t"
            << print_hex(str.c_str(), str.length()) << std::endl;

  auto self(shared_from_this());
  boost::asio::async_write(
      socket_, boost::asio::buffer(str),
      [this, self](boost::system::error_code ec, std::size_t length) {
        if (!ec) {
          do_write();
        } else {
          // TODO handle disconnect
          gateway_->remove_client(this->addr_);
        }
      });
}

void session::process(std::size_t length) {
  boost::interprocess::bufferstream data(data_, length);

  switch (data.peek()) {
  case 0x02:
  case 0x04:
  case 0x06:
  case 0x10: {
    uncompressed_packet p;
    p.read(data);
    // queue p
    break;
  }
  case 0x08:
  case 0x0e:
  case 0x18: {
    zlib1_packet p;
    p.read(data);
    // queue p
    break;
  }
  case 0x0c:
  case 0x12:
  case 0x14:
  case 0x16: {
    zlib2_packet p;
    p.read(data);
    // queue p
    break;
  }
  case 0x0a:
  case 0x1a: {
    zlib3_packet p;
    p.read(data);
    // queue p
    send(p.msg);
    break;
  }
  }
}

void gateway::do_accept() {
  acceptor_.async_accept(
      [this](boost::system::error_code ec, tcp::socket socket) {
        if (!ec) {
          std::array<char, 3> addr{0, 0, 0}; // TODO generate 3 random bytes
          auto client = std::make_shared<session>(addr, std::move(socket), this);

          add_client(addr, client);
          client->start();
        }

        do_accept();
      });
}

void gateway::add_client(std::array<char, 3> addr, std::weak_ptr<session> s) {
  std::lock_guard<std::mutex> lk(mx_);
  clients_.insert(std::make_pair(addr, s));
}

void gateway::remove_client(std::array<char, 3> addr) {
  std::lock_guard<std::mutex> lk(mx_);
  clients_.erase(addr);
}

void gateway::broadcast(message msg) {
  std::lock_guard<std::mutex> lk (mx_);
  for (const auto& client : clients_) {
    auto session = client.second.lock();
    if (session) {
      session->send(msg);
    }
  }
}
