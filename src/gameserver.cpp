#include <gateway.h>
#include <iostream>
#include <thread>

int main(int argc, char *argv[]) {
  try {
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
