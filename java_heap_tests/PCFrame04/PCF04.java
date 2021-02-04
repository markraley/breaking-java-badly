import java.util.LinkedList;
import java.util.Queue;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
// import static java.lang.System.out;

public class PCF04 {

  static final int Million = (1024*1024);

  public static void pf(String fmt, Object... args)
  {
    System.out.printf(fmt, args);
  }

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
    int size = Integer.parseInt(args[0]) * Million;
    int num_count = Integer.parseInt(args[1]) * Million;
    Buffer buffer = new Buffer(size);
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
      metrics_size = Math.round(num_count / (8 * Million));
      metrics_arr = new int[metrics_size];

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

          if (counter > 8 * Million)  {
            double elapsed_min = (System.currentTimeMillis() - start_time)/(1000.0*60.0);

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
            pf("%d\n", value);
            pf("elapsed time: %f\n",
                (System.currentTimeMillis() - start_time)/1000.0);
            pf("MQD:", metrics_arr[metrics_size/2]);

            for (int i = 0; i < metrics_size; i++)
              pf("\t%d\n", metrics_arr[i]);

            System.exit(0);
          }
          notify();
        }
      }
    }
  }
}