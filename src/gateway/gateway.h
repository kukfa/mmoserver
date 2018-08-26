#pragma once

#include <boost/asio.hpp>
#include <constants.h>
#include <messages.h>
#include <packets.h>
#include <zmq.hpp>

using boost::asio::ip::tcp;

class gateway {
public:
  gateway(boost::asio::io_context &io_context, std::string ip, int port,
          std::string broker_addr)
      : acceptor_(
            io_context,
            tcp::endpoint(boost::asio::ip::address::from_string(ip), port)),
        broker_addr_(broker_addr) {
    do_accept();
  }

private:
  void do_accept();

  tcp::acceptor acceptor_;
  std::string broker_addr_;
};
