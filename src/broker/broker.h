#pragma once

#include <constants.h>
#include <packets.h>
#include <zmq.hpp>

class example_service {
public:
  example_service(addr addr)
      : ctx_(1), broker_(ctx_, ZMQ_DEALER), addr_(addr) {}

  void work();

private:
  zmq::context_t ctx_;
  zmq::socket_t broker_;
  addr addr_;
  char data_[max_length];
};

class broker {
public:
  broker() : ctx_(1), broker_(ctx_, ZMQ_ROUTER) {}

  void run();

private:
  zmq::context_t ctx_;
  zmq::socket_t broker_;
  char data_[max_length];
};
