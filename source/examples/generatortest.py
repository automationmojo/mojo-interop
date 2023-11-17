

def connection_generator():

    index = 0

    for index in range(39):

        try:

            yield index + 1

        except Exception as toerr:

            print("Got our timeout.")



def main_test():

    gen = connection_generator()

    while index := gen.send(None):

        try:
            if index % 5 == 0:
                raise TimeoutError("Simulated Timeout")
            elif index == 29:
                gen.close()
            else:
                print(index)

        except Exception as xcpt:
            gen.throw(xcpt)

    print("Done")



if __name__ == "__main__":
    main_test()
