#include <broker.h>
#include <iostream>

void example_service::work() {
  broker_.setsockopt(ZMQ_IDENTITY, addr_.data(), addr_.size());
  broker_.connect("tcp://localhost:31337");

  try {
    while (true) {
      zmq::message_t identity;
      broker_.recv(&identity);
      auto len = broker_.recv(data_, max_length);
      std::cout << "RECV [" << print_hex((char *)addr_.data(), addr_.size())
                << "]<-[" << print_hex((char *)identity.data(), identity.size())
                << "]\t" << print_hex(data_, len) << std::endl;

      std::cout << "SEND [" << print_hex((char *)addr_.data(), addr_.size())
                << "]->[" << print_hex((char *)identity.data(), identity.size())
                << "]\t" << print_hex(data_, len) << std::endl;
      broker_.send(identity, ZMQ_SNDMORE);
      broker_.send(data_, len);
    }
  } catch (std::exception &e) {
  }
}

void broker::run() {
  broker_.bind("tcp://*:31337");

  while (1) {
    zmq::message_t src;
    broker_.recv(&src);
    zmq::message_t dest;
    broker_.recv(&dest);
    auto len = broker_.recv(data_, max_length);

    broker_.send(dest, ZMQ_SNDMORE);
    broker_.send(src, ZMQ_SNDMORE);
    broker_.send(data_, len);
  }
}
