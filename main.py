#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021-2022 Bosch Rexroth AG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import time
from token import NUMBER

import ctrlxdatalayer
from ctrlxdatalayer.variant import Variant, Result

from helper.ctrlx_datalayer_helper import get_provider

from app.my_provider_node import SQLiteNode
from app.app_data_control import AppDataControl

NUMBER_OF_TERMINALS = 4 #define the number of terminals required. 

# addresses of provided values
address_base = "SQLite/"
type_address_string = "types/datalayer/string"


def main():
    print 
    with ctrlxdatalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        # ip="10.0.2.2", ssl_port=8443: ctrlX virtual with port forwarding and default port mapping
        provider, connection_string = get_provider(
            datalayer_system, ip="10.0.2.2", ssl_port=8443)
        if provider is None:
            print("ERROR Connecting", connection_string, "failed.")
            sys.exit(1)

        #if not os.path.exists("/var/snap/rexroth-solutions/common/solutions/activeConfiguration/SQLite"):
        #    os.mkdir("/var/snap/rexroth-solutions/common/solutions/activeConfiguration/SQLite")
        if not os.path.exists(os.environ('SNAP_COMMON') + "/solutions/activeConfiguration/SQLite"):
            os.mkdir(os.environ('SNAP_COMMON') + "/solutions/activeConfiguration/SQLite")

        with provider:  # provider.close() is called automatically when leaving with... block

            result = provider.start()
            if result != Result.OK:
                print("ERROR Starting Data Layer Provider failed with:", result)
                return

            # Path to compiled files
            snap_path = os.getenv('SNAP')
            provider_node = []
            provider_node = [0 for i in range(NUMBER_OF_TERMINALS)]

            for i in range(NUMBER_OF_TERMINALS):
                provider_node[i] = provide_string(provider, "Terminal_" + str(i))
            
            #config = AppDataControl()

            print("INFO Running endless loop...")
            while provider.is_connected():
                time.sleep(1.0)  # Seconds

            print("ERROR Data Layer Provider is disconnected")

            for i in provider_node:
                i.unregister_node()
                del i
            #provider_node_str.unregister_node()
            #del provider_node_str

            print("Stopping Data Layer provider:", end=" ")
            result = provider.stop()
            print(result)

        # Attention: Doesn't return if any provider or client instance is still running
        stop_ok = datalayer_system.stop(False)
        print("System Stop", stop_ok)


def provide_string(provider: ctrlxdatalayer.provider, name: str):
    # Create and register simple string provider node
    print("Creating string  provider node " + address_base + name)
    variantString = Variant()
    variantString.set_string("Enter SQL script here. Use ';' as the last character to suppress result")
    provider_node_str = SQLiteNode(
        provider, 
        type_address_string,
        address_base + name, 
        name, 
        "-",
        "SQL-Terminal",
        variantString)
    result = provider_node_str.register_node()
    if result != ctrlxdatalayer.variant.Result.OK:
        print("ERROR Registering node " + address_base +
              name + " failed with:", result)

    return provider_node_str


if __name__ == '__main__':
    main()
