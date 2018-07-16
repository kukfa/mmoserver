#include <boost/interprocess/streams/bufferstream.hpp>
#include <gateway.h>
#include <iomanip>
#include <iostream>
#include <packets.h>
#include <utils.h>

using boost::asio::ip::tcp;

void session::start() { do_read(); }

void session::do_read() {
  auto self(shared_from_this());
  socket_.async_read_some(
      boost::asio::buffer(data_, max_length),
      [this, self](boost::system::error_code ec, std::size_t length) {
        if (!ec) {
          process(length);
        }
      });
}

void session::do_write(std::size_t length) {
  auto self(shared_from_this());
  boost::asio::async_write(
      socket_, boost::asio::buffer(data_, length),
      [this, self](boost::system::error_code ec, std::size_t /*length*/) {
        if (!ec) {
          do_read();
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
    break;
  }
  }

  do_write(length);
}

void gateway::do_accept() {
  acceptor_.async_accept(
      [this](boost::system::error_code ec, tcp::socket socket) {
        if (!ec) {
          std::make_shared<session>(std::move(socket))->start();
        }

        do_accept();
      });
}
