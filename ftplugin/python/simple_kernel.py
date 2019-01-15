import queue
from pprint import PrettyPrinter

from jupyter_client import KernelManager, find_connection_file
from jupyter_client.manager import start_new_kernel


class SimpleKernel(object):
    """
    ## Description
    **SimpleKernel**:
     A simplistic Jupyter kernel client wrapper.

    Additional information in [this GitHub issue]
    (

    )
    """

    def __init__(self, use_exist=False):
        """
        ## Description
        Initializes the `kernel_manager` and `client` objects
        and starts the kernel. Also initializes the pretty printer
        for displaying object properties and execution result
        payloads.

        ## Parameters
        None.
        """
        if not use_exist:
            # Initialize kernel and client
            self.kernel_manager, self.client = start_new_kernel()
            self.send = self.client.execute
        else:
            self.kernel_manager = KernelManager(
                connection_file=find_connection_file())
            self.kernel_manager.load_connection_file(find_connection_file())
            self.client = self.kernel_manager.client()
            self.client.start_channels()
            self.send = self.client.execute

        # Initialize pretty printer
        self.pp = PrettyPrinter(indent=2)

    # end __init__ ##

    def execute(self, code):
        """
        ## Description
        **execute**:
        Executes a code string in the kernel. Can return either
        the full execution response payload, or just `stdout`. Also,
        there is a verbose mode that displays the execution process.

        ## Parameters
        code : string
            The code string to get passed to `stdin`.
        verbose : bool (default=False)
            Whether to display processing information.
        get_type : bool (default=False) NOT IMPLEMENTED
            When implemented, will return a dict including the output
            and the type. E.g.

            1+1 ==> {stdout: 2, type: int}
            "hello" ==> {stdout: "hello", type: str}
            print("hello") ==> {stdout: "hello", type: NoneType}
            a=10 ==> {stdout: None, type: None}

        ## Returns
        `stdout` or the full response payload.
        """

        # Execute the code
        self.client.execute(code)

        # Continue polling for execution to complete
        list_io_msg = []
        while True:
            # Poll the message
            try:
                io_msg_content = self.client.get_iopub_msg(timeout=0.2)['content']
                list_io_msg.append(io_msg_content)
            except queue.Empty:
                break

        if len(list_io_msg) < 3:
            temp = ''
        else:
            temp = list_io_msg[-2]

        # print(temp)
        # Check the message for various possibilities
        if 'data' in temp:  # Indicates completed operation
            out = temp['data']['text/plain']
        elif 'name' in temp and temp['name'] == "stdout":  # indicates output
            out = temp['text']
        elif 'traceback' in temp:  # Indicates error
            print("ERROR")
            out = '\n'.join(temp['traceback'])  # Put error into nice format
        else:
            out = ''

        return out

    def __del__(self):
        """
        ## Description
        Destructor. Shuts down kernel safely.
        """
        self.kernel_manager.shutdown_kernel()


# end Simple Kernel #


def test(use_exist=True):
    import time

    kernel = SimpleKernel(use_exist)

    commands = [
        '1+1',
        'a=5',
        'b=0',
        'b',
        'print()',
        'print("hello there")',
        '10',
        'a*b',
        'a',
        'a+b',
        's = "this is s"',
        'print(s)',
        'type(s)',
        'type(a)',
        'type(1.0*a)',
        'print(a+b)',
        'print(a*10)',
        'c=1/b',
        'd = {"a":1,"b":"Two","c":[1,2,3]}',
        'd',
        'import json',
        'j = json.loads(str(d).replace(\"\\\'\",\"\\"\"))',
        'j',
        'import pandas as pd',
        'df = pd.DataFrame(dict(A=[1,2,3], B=["one", "two", "three"]))',
        'df',
        'df.describe()'
    ]

    for command in commands:
        print(">>> " + command)
        out = kernel.execute(command)
        if out:
            print(out)

    time.sleep(10)


if __name__ == "__main__":
    test(True)
    # test(False)
