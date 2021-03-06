import java.util.LinkedList;
import java.util.Queue;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// Producer Consumer Framework, 4th version
public class PCFrame04 {

  private static class ProducerThread extends Thread {
      private Buffer buf;
      private int num_count;
      public ProducerThread(Buffer b, int num_count) {
        this.buf = b;
        this.num_count = num_count;
      }

      @Override
      public void run() {
        try {
          buf.produce(num_count);
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
  }

  private static class ConsumerThread extends Thread {
      private Buffer buf;
      private int num_count;
      public ConsumerThread(Buffer b, int num_count) {
        this.buf = b;
        this.num_count = num_count;
      }

      @Override
      public void run() {
        try {
          buf.consume(num_count);
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
  }

  public static void main(String[] args) throws InterruptedException {
//        Buffer buffer = new Buffer(57*1024*1024);
    System.out.println(args[0]);
    int size = Integer.parseInt(args[0]) * 1024*1024;
    int num_count = Integer.parseInt(args[1]) * 1024*1024;
    System.out.println(size);
    Buffer buffer = new Buffer(size);
//        Buffer buffer = new Buffer(1*1024*1024);
    Thread producerThread = new ProducerThread(buffer, num_count);
    Thread consumerThread = new ConsumerThread(buffer, num_count);
    consumerThread.start();
    producerThread.start();
    consumerThread.join();
    producerThread.join();

    System.exit(0);

  }
  static class Buffer {
    private Queue<Integer> list;

    private int[] metrics_arr;
    private int metrics_size;

    private int capacity;

    public Buffer(int capacity) {
      this.list = new LinkedList<>();
      this.capacity = capacity;
    }
    public void produce(int num_count) throws InterruptedException {
      double start_time = System.currentTimeMillis();
      int value = 0;
      int counter = 0;
      int index = 0;
      metrics_size = Math.round(num_count / (8 * 1024 * 1024));
      metrics_arr = new int[metrics_size];
      System.out.println(metrics_size);

      while (true) {
        synchronized (this) {
          while (list.size() >= capacity) {
            // wait for the consumer
            wait();
          }

          list.add(value);
          value++;
          counter++;

          // notify the consumer
          notify();

          if (counter > 8*1024*1024)  {
            double elapsed_min =
                      (System.currentTimeMillis() - start_time)
                        / (1000.0 * 60.0);
            counter = 0;
            if (index >= 0 && index < metrics_size)
              metrics_arr[index++] = list.size();
          }
        }
      }
    }

    public void consume(int num_count) throws InterruptedException {
      double start_time = System.currentTimeMillis();
      int value = 0;
      int counter = 0;
      while (true) {
        synchronized (this) {
          while (list.size() == 0) {
            // wait for the producer
            wait();
          }

          value = list.poll();
          counter++;

          if (value >= num_count) {
            Arrays.sort(metrics_arr);
            System.out.println(value);
            System.out.println("elapsed time: "
                    + (System.currentTimeMillis() - start_time)/1000.0);
            System.out.println("median queue size observed:"
              + metrics_arr[metrics_size/2]);

//                        for (int i = 0; i < metrics_size; i++)
//                            System.out.println(metrics_arr[i]);

            System.exit(0);
          }

          // notify the producer
          notify();
        }
      }
    }
  }
}