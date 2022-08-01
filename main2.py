#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Bosch Rexroth AG
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
#from sqlite3.dbapi2 import Connection
import time
#import sqlite3
#from sqlite3 import Error

import ctrlxdatalayer
from ctrlxdatalayer.variant import Variant

#from helper.ctrlx_datalayer_helper import get_provider

from app.sql_provider_node import SQLiteNode

value_address_str_1 = "terminal-1"
value_address_str_2 = "terminal-2"
value_address_str_3 = "terminal-3"
value_address_str_4 = "terminal-4"

# addresses of provided values
address_base = "SQLite/"
type_address_string = "types/datalayer/string"

def main():


    with ctrlxdatalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        connectionProvider = "DL_IPC_AUTO"# "tcp://boschrexroth:boschrexroth@192.168.1.1:2070"

        if 'SNAP' in os.environ:
            connectionProvider = "ipc://"

        print("Connecting", connectionProvider)
        with datalayer_system.factory().create_provider(connectionProvider) as provider:
            result = provider.start()
            if result is not ctrlxdatalayer.variant.Result.OK:
                print("ERROR Starting Data Layer Provider failed with:", result)
                return

            provider_node_str_1 = provide_string(provider, value_address_str_1)
            provider_node_str_2 = provide_string(provider, value_address_str_2)
            provider_node_str_3 = provide_string(provider, value_address_str_3)
            provider_node_str_4 = provide_string(provider, value_address_str_4)

            print("Running endless loop...")
            while provider.is_connected():
                time.sleep(1.0)  # Seconds

            print("ERROR Data Layer Provider is disconnected")

            print("Stopping Data Layer Provider: ", end=" ")
            result = provider.stop()
            print(result)

            print("Unregister provider Node", value_address_str_1, end=" ")
            result = provider.unregister_node(value_address_str_1)
            print(result)

            print("Unregister provider Node", value_address_str_2, end=" ")
            result = provider.unregister_node(value_address_str_2)
            print(result)
            
            print("Unregister provider Node", value_address_str_3, end=" ")
            result = provider.unregister_node(value_address_str_3)
            print(result)
            
            print("Unregister provider Node", value_address_str_4, end=" ")
            result = provider.unregister_node(value_address_str_4)
            print(result)

            del provider_node_str_1
            del provider_node_str_2
            del provider_node_str_3
            del provider_node_str_4

        datalayer_system.stop(True)

def provide_string(provider: ctrlxdatalayer.provider, name):
    # Create and register simple string provider node
    print("Creating string  provider node")
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
