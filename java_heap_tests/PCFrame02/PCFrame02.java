import java.util.LinkedList;
import java.util.Queue;
import java.util.ArrayList;
import java.util.List;

public class PCFrame02 {

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
                    buf.produce();
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

/*

        List <ProducerThread> prod_arr = new ArrayList<ProducerThread>();

        int pcount = 1;
        for (int i = 0; i < pcount; i++) {
            prod_arr.add(new ProducerThread(buffer));
        }
        consumerThread.start();
        for (int i = 0; i < pcount; i++) {
            prod_arr.get(i).start();
        }
        for (int i = 0; i < pcount; i++) {
            prod_arr.get(i).join();
        }
*/
    }
    static class Buffer {
        private Queue<Integer> list;
        private int capacity;
        public Buffer(int capacity) {
            this.list = new LinkedList<>();
            this.capacity = capacity;
        }
        public void produce() throws InterruptedException {
            int value = 0;
            while (true) {
                synchronized (this) {
                    while (list.size() >= capacity) {
                        // wait for the consumer
                        wait();
                    }

                    for (int i = 0; i < 1; i++) {
                        list.add(value);
                        value++;
                    }
                    // notify the consumer
                    notify();
//                    Thread.sleep(1);
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

//                    if (list.size() == 0) {
//                        System.out.println("fail");
//                    }

                    value = list.poll();
                    counter++;
                    if (counter > 32*1024*1024)  {
                        double elapsed_min = (System.currentTimeMillis() - start_time)/(1000.0*60.0);
                        System.out.println(value + " " + elapsed_min + " " + (value / elapsed_min) + " " + list.size());
                        counter = 0;
                    }
                    if (value >= num_count) {
                        System.out.println(value);
                        System.out.println("elapsed time: " + (System.currentTimeMillis() - start_time)/1000.0);
                        System.exit(0);
                    }
//                    System.out.println("Consume " + value + " " + list.size());
                    // notify the producer
                    notify();
//                    Thread.sleep(1);
                }
            }
        }
    }
}