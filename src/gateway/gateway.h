#pragma once

#include <boost/asio.hpp>
#include <constants.h>
#include <messages.h>
#include <packets.h>
#include <zmq.hpp>

using boost::asio::ip::tcp;

class gateway;
class session : public std::enable_shared_from_this<session> {
public:
  session(std::array<char, 3> addr, tcp::socket socket)
      : addr_(addr), socket_(std::move(socket)), ctx_(1),
        broker_(ctx_, ZMQ_DEALER){};
  void start();

private:
  void read_client();
  void write_client(std::size_t length);
  void read_broker();
  void write_broker(std::size_t length);

  tcp::socket socket_;
  addr addr_;
  char data_[max_length];
  zmq::context_t ctx_;
  zmq::socket_t broker_;
};

class gateway {
public:
  gateway(boost::asio::io_context &io_context, short port)
      : acceptor_(io_context, tcp::endpoint(tcp::v4(), port)) {
    do_accept();
  }

private:
  void do_accept();

  tcp::acceptor acceptor_;
};
