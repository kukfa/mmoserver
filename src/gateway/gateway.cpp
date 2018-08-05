#include <boost/interprocess/streams/bufferstream.hpp>
#include <gateway.h>
#include <iostream>
#include <packets.h>
#include <utils.h>
#include <zmq.hpp>

using boost::asio::ip::tcp;

void session::start() {
  broker_.setsockopt(ZMQ_IDENTITY, addr_.data(), addr_.size());
  broker_.connect("tcp://localhost:31337");

  read_client();
}

void session::read_client() {
  auto self(shared_from_this());
  socket_.async_read_some(
      boost::asio::buffer(data_, max_length),
      [this, self](boost::system::error_code ec, std::size_t length) {
        std::cout << "RECV " << print_hex(addr_.data(), addr_.size())
                  << "\t\t\t" << print_hex(data_, length) << std::endl;
        if (!ec) {
          write_broker(length);
        } else {
          // TODO handle disconnect
        }
      });
}

void session::write_client(std::size_t length) {
  std::cout << "SEND " << print_hex(addr_.data(), addr_.size()) << "\t\t\t"
            << print_hex(data_, length) << std::endl;

  auto self(shared_from_this());
  boost::asio::async_write(
      socket_, boost::asio::buffer(data_, length),
      [this, self](boost::system::error_code ec, std::size_t length) {
        if (!ec) {
          read_client();
        } else {
          // TODO handle disconnect
        }
      });
}

void session::read_broker() {
  zmq::pollitem_t items[] = {broker_, 0, ZMQ_POLLIN, 0};
  zmq::poll(items, 1, 10);
  if (items[0].revents & ZMQ_POLLIN) {
    zmq::message_t identity;
    broker_.recv(&identity);
    auto len = broker_.recv(data_, max_length);
    std::cout << "RECV [" << print_hex(addr_.data(), addr_.size()) << "]<-["
              << print_hex((char *)identity.data(), identity.size()) << "]\t"
              << print_hex(data_, len) << std::endl;
    write_client(len);
  }
  read_client();
}

void session::write_broker(std::size_t length) {
  boost::interprocess::bufferstream packet(data_, length);
  boost::interprocess::bufferstream msg(data_, max_length);

  switch (packet.peek()) {
  case 0x02:
  case 0x04:
  case 0x06:
  case 0x10: {
    uncompressed_packet p;
    p.read(packet);
    auto len = p.msg.write(msg);
    zmq::message_t identity(p.dest.data(), p.dest.size(), nullptr);
    std::cout << "SEND [" << print_hex(addr_.data(), addr_.size()) << "]->["
              << print_hex((char *)identity.data(), identity.size()) << "]\t"
              << print_hex(data_, len) << std::endl;
    broker_.send(identity, ZMQ_SNDMORE);
    broker_.send(data_, len);
  }
  case 0x08:
  case 0x0e:
  case 0x18: {
    zlib1_packet p;
    p.read(packet);
    auto len = p.msg.write(msg);
    zmq::message_t identity(p.dest.data(), p.dest.size(), nullptr);
    std::cout << "SEND [" << print_hex(addr_.data(), addr_.size()) << "]->["
              << print_hex((char *)identity.data(), identity.size()) << "]\t"
              << print_hex(data_, len) << std::endl;
    broker_.send(identity, ZMQ_SNDMORE);
    broker_.send(data_, len);
  }
  case 0x0c:
  case 0x12:
  case 0x14:
  case 0x16: {
    zlib2_packet p;
    p.read(packet);
    auto len = p.msg.write(msg);
    zmq::message_t identity(p.dest.data(), p.dest.size(), nullptr);
    std::cout << "SEND [" << print_hex(addr_.data(), addr_.size()) << "]->["
              << print_hex((char *)identity.data(), identity.size()) << "]\t"
              << print_hex(data_, len) << std::endl;
    broker_.send(identity, ZMQ_SNDMORE);
    broker_.send(data_, len);
  }
  case 0x0a:
  case 0x1a: {
    zlib3_packet p;
    p.read(packet);
    auto len = p.msg.write(msg);
    zmq::message_t identity(p.dest.data(), p.dest.size(), nullptr);
    std::cout << "SEND [" << print_hex(addr_.data(), addr_.size()) << "]->["
              << print_hex((char *)identity.data(), identity.size()) << "]\t"
              << print_hex(data_, len) << std::endl;
    broker_.send(identity, ZMQ_SNDMORE);
    broker_.send(data_, len);
  }
  }

  read_broker();
}

void gateway::do_accept() {
  acceptor_.async_accept(
      [this](boost::system::error_code ec, tcp::socket socket) {
        if (!ec) {
          addr identity{0, 0, 0}; // TODO generate 3 random bytes
          auto client = std::make_shared<session>(identity, std::move(socket));

          client->start();
        }

        do_accept();
      });
}
