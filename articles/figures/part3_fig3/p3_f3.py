import json
import matplotlib

def main():
    with open('test.json', 'r') as myfile:
        ds1 =myfile.read()

    ds1_obj = json.loads(ds1)

    matplotlib.use('Agg')
    import pylab

    fig,ax = pylab.subplots(1)
#   fig.set_size_inches(8,6)

    x_arr, y_arr = [], []
    ox_arr, oy_arr, run_arr = [], [], []
    run_num = 1

    for obj in ds1_obj:
        x, y = obj['x'],obj['y']
        x_arr.append(x)
        y_arr.append(y)

        if (x > 700):
            ox_arr.append(x)
            oy_arr.append(y)
            run_arr.append(run_num)

        run_num += 1

    pylab.title("Producer-Consumer Test One\n"
                "36M MCL - 72 total runs\n"
                "Linked List - Parallel Old"
        )

    pylab.xlabel('test run time (seconds)')
    pylab.ylabel('Median Observed Queue Size (K)')

    pylab.scatter(x_arr, y_arr, marker='.')

    for i in range(len(ox_arr)):
#       ax.plot(ox_arr[i], oy_arr[i], marker='+', color='green')
        ax.annotate(str(run_arr[i]), xy=(ox_arr[i], oy_arr[i] ), size=10)

    # sub title

    text_str = 'Figure Three'
    ann = ax.annotate(text_str, xy=(.05, .01 ),
                        xycoords="figure fraction", size=11)

    pylab.subplots_adjust(bottom=.12)
    pylab.show()
    print('figure size', fig.get_size_inches())
    pylab.savefig("p3_f3.png", dpi=100)

if __name__ == '__main__':
    main()
