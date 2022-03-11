import multiprocessing as mp

def worker(working_queue, output_queue):
    while True:
        try:
            if working_queue.empty() is True:
                break  
            else:
                picked = working_queue.get_nowait()
                if picked % 2 == 0: 
                        output_queue.put(picked)
                else:
                    working_queue.put(picked+1)
        except Exception:
            continue

    return

if __name__ == '__main__':
    #Manager seem to be unnecessary.
    #manager = mp.Manager()
    #working_q = manager.Queue()

    working_q = mp.Queue()
    output_q = mp.Queue()
    static_input = range(100)     
    for i in static_input:
        working_q.put(i)
    processes = [mp.Process(target=worker,args=(working_q, output_q)) for i in range(mp.cpu_count())]
    print("len processes: ", len(processes))
    for proc in processes:
        proc.start()
    for proc in processes:
        proc.join()
    results_bank = []
    while True:
       if output_q.empty() is True:
           print("breaking")
           break
       results_bank.append(output_q.get_nowait())
    print("len results bank: ", len(results_bank)) # length of this list should be equal to static_input, which is the range used to populate the input queue. In other words, this tells whether all the items placed for processing were actually processed.
    results_bank.sort()
    print(results_bank)