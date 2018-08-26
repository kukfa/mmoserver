#include <gateway.h>
#include <iostream>
#include <libconfig.h++>
#include <session.h>

using boost::asio::ip::tcp;

int main(int argc, char *argv[]) {
  libconfig::Config cfg;
  cfg.readFile("config.cfg");
  const libconfig::Setting &servers = cfg.getRoot()["gameservers"];
  auto server_name = argc > 1 ? argv[1] : "primary";
  const libconfig::Setting &server = servers[server_name];

  std::string ip;
  int gateway_port, broker_port;
  server.lookupValue("ip", ip);
  server.lookupValue("gateway_port", gateway_port);
  server.lookupValue("broker_port", broker_port);
  auto broker_addr = ip + ":" + std::to_string(broker_port);

  boost::asio::io_context io_context;
  gateway g(io_context, ip, gateway_port, broker_addr);
  io_context.run();

  return 0;
}

void gateway::do_accept() {
  acceptor_.async_accept([this](boost::system::error_code ec,
                                tcp::socket socket) {
    if (!ec) {
      message_addr identity{0, 0, 0}; // TODO generate 3 random bytes
      auto client =
          std::make_shared<session>(std::move(socket), identity, broker_addr_);

      client->start();
    }

    do_accept();
  });
}
