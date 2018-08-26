#pragma once

#include <constants.h>
#include <packets.h>
#include <zmq.hpp>

class example_service {
public:
  example_service(message_addr identity, std::string broker_addr)
      : ctx_(1), broker_(ctx_, ZMQ_DEALER), identity_(identity),
        broker_addr_(broker_addr) {}

  void run();

private:
  zmq::context_t ctx_;
  zmq::socket_t broker_;
  message_addr identity_;
  std::string broker_addr_;
  char data_[max_length];
};
