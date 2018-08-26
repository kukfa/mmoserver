#include <broker.h>
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

  broker br(broker_addr);
  br.run();

  return 0;
}

void broker::run() {
  broker_.bind("tcp://" + broker_addr_);

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
