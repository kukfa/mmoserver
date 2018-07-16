#pragma once

#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class session : public std::enable_shared_from_this<session> {
public:
  enum { max_length = 1048576 }; // max in DFCSocketChannel::updateReceiveQueue
  session(tcp::socket socket) : socket_(std::move(socket)){};
  void start();

private:
  void do_read();
  void do_write(std::size_t length);
  void process(std::size_t length);

  tcp::socket socket_;
  char data_[max_length];
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
