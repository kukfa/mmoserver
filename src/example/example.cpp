#include <example.h>
#include <iostream>
#include <libconfig.h++>

int main(int argc, char *argv[]) {
  libconfig::Config cfg;
  cfg.readFile("config.cfg");
  const libconfig::Setting &servers = cfg.getRoot()["gameservers"];
  auto server_name = argc > 1 ? argv[1] : "primary";
  const libconfig::Setting &server = servers[server_name];

  std::string ip;
  int broker_port;
  server.lookupValue("ip", ip);
  server.lookupValue("broker_port", broker_port);
  auto broker_addr = ip + ":" + std::to_string(broker_port);

  message_addr identity = {(char)0xdd, (char)0x7b, 0x00};
  example_service srv{identity, broker_addr};
  srv.run();

  return 0;
}

void example_service::run() {
  broker_.setsockopt(ZMQ_IDENTITY, identity_.data(), identity_.size());
  broker_.connect("tcp://" + broker_addr_);

  try {
    while (true) {
      zmq::message_t identity;
      broker_.recv(&identity);
      auto len = broker_.recv(data_, max_length);
      std::cout << "RECV ["
                << print_hex((char *)identity_.data(), identity_.size())
                << "]<-[" << print_hex((char *)identity.data(), identity.size())
                << "]\t" << print_hex(data_, len) << std::endl;

      std::cout << "SEND ["
                << print_hex((char *)identity_.data(), identity_.size())
                << "]->[" << print_hex((char *)identity.data(), identity.size())
                << "]\t" << print_hex(data_, len) << std::endl;
      broker_.send(identity, ZMQ_SNDMORE);
      broker_.send(data_, len);
    }
  } catch (std::exception &e) {
  }
}
