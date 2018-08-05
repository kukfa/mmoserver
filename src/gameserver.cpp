#include <broker.h>
#include <gateway.h>
#include <iostream>
#include <packets.h>
#include <thread>

int main(int argc, char *argv[]) {
  try {
    std::thread broker_thread([] {
      broker br;
      br.run();
    });
    broker_thread.detach();

    std::thread service_thread([] {
      addr ex = {(char)0xdd, (char)0x7b, 0x00};
      example_service srv{ex};
      srv.work();
    });
    service_thread.detach();

    std::thread gateway_thread([] {
      boost::asio::io_context io_context;
      gateway g(io_context, 7777);
      io_context.run();
    });
    gateway_thread.detach();

    while (true) {
      // TODO game loop
      std::this_thread::sleep_for(std::chrono::seconds(1));
    }
  } catch (std::exception &e) {
    std::cerr << "Exception: " << e.what() << "\n";
  }

  return 0;
}
