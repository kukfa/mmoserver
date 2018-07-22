#pragma once

#include <boost/asio.hpp>
#include <messages.h>
#include <queue>

using boost::asio::ip::tcp;

class gateway;
class session : public std::enable_shared_from_this<session> {
public:
  enum { max_length = 1048576 }; // max in DFCSocketChannel::updateReceiveQueue
  session(std::array<char, 3> addr, tcp::socket socket, gateway* gateway)
      : addr_(addr), socket_(std::move(socket)), gateway_(gateway) {};
  void start();
  void send(message msg);

private:
  void do_read();
  void do_write();
  void process(std::size_t length);

  gateway* gateway_;
  tcp::socket socket_;
  std::array<char, 3> addr_;
  std::queue<message> send_queue_;
  char data_[max_length];
};

class gateway {
public:
  gateway(boost::asio::io_context &io_context, short port)
      : acceptor_(io_context, tcp::endpoint(tcp::v4(), port)) {
    do_accept();
  }

  void add_client(std::array<char, 3> addr, std::weak_ptr<session> s);
  void remove_client(std::array<char, 3> addr);
  void broadcast(message msg);

private:
  void do_accept();

  tcp::acceptor acceptor_;
  std::mutex mx_;
  std::map<std::array<char, 3>, std::weak_ptr<session>> clients_;
};
