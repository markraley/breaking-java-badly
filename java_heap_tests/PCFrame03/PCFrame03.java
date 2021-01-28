import java.util.ArrayDeque;
import java.util.Queue;

public class PCFrame03 {

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
		System.out.println(args[0]);
		int size = Integer.parseInt(args[0]) * 1024*1024;
		int num_count = Integer.parseInt(args[1]) * 1024*1024;
		System.out.println("PCFrame03");
		System.out.println(size);

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
		private Queue<Integer> buf;
		private int capacity;

		public Buffer(int capacity) {
			this.buf = new ArrayDeque<>();
			this.capacity = capacity;
		}

		public void produce() throws InterruptedException {
			int value = 0;
			while (true) {
				synchronized (this) {
					if (capacity != 0) {
						while (buf.size() >= capacity) {
							// wait for the consumer
							wait();
						}
					}

					buf.add(value++);

					// notify the consumer
					notify();
				}
			}
		}

		public void consume(int num_count) throws InterruptedException {
			double start_time = System.currentTimeMillis();
			int value = 0;
			int counter = 0;
			double elapsed_min;
			double cur_time;

			while (true) {
				synchronized (this) {
					while (buf.size() == 0) {
						// wait for the producer
						wait();
					}

					value = buf.poll();
					counter++;

					cur_time = System.currentTimeMillis();
					if (counter > 32*1024*1024)  {
						elapsed_min = (cur_time - start_time)/(1000.0*60.0);
						System.out.println(value + " " + elapsed_min
							+ " " + (value / elapsed_min) + " " + buf.size());
						counter = 0;
					}

					if (value >= num_count) {
						System.out.println(value);
						System.out.println("elapsed time: "
							+ (cur_time - start_time)/1000.0);
						System.exit(0);
					}
					notify();
				}
			}
		}
	}
}