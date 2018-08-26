#pragma once

#include <boost/asio.hpp>
#include <constants.h>
#include <messages.h>
#include <packets.h>
#include <zmq.hpp>

using boost::asio::ip::tcp;

class session : public std::enable_shared_from_this<session> {
public:
  session(tcp::socket socket, message_addr identity, std::string broker_addr)
      : ctx_(1), broker_(ctx_, ZMQ_DEALER), socket_(std::move(socket)),
        identity_(identity), broker_addr_(broker_addr) {}
  void start();

private:
  void read_client();
  void write_client(std::size_t length);
  void read_broker();
  void write_broker(std::size_t length);

  zmq::context_t ctx_;
  zmq::socket_t broker_;
  tcp::socket socket_;
  message_addr identity_;
  std::string broker_addr_;
  char data_[max_length];
};
