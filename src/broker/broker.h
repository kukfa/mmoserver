#pragma once

#include <constants.h>
#include <packets.h>
#include <zmq.hpp>

class broker {
public:
  broker(std::string broker_addr)
      : ctx_(1), broker_(ctx_, ZMQ_ROUTER), broker_addr_(broker_addr) {}

  void run();

private:
  zmq::context_t ctx_;
  zmq::socket_t broker_;
  std::string broker_addr_;
  char data_[max_length];
};
