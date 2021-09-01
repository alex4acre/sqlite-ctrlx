# MIT License
#
# Copyright (c) 2021, Bosch Rexroth AG
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

import json
import os
from sqlite3.dbapi2 import Connection
import datalayer.clib
import datalayer
from datalayer.provider_node import ProviderNodeCallbacks, NodeCallback
from datalayer.variant import Result, Variant, VariantType

import sqlite3
from sqlite3 import Error
import flatbuffers
from comm.datalayer import Metadata
from comm.datalayer import AllowedOperations
from comm.datalayer import Reference




class SQLiteNode:

    def __init__(self,provider : datalayer.provider, address : str , initialValue: Variant):

        self.cbs = ProviderNodeCallbacks(
            self.__on_create,
            self.__on_remove,
            self.__on_browse,
            self.__on_read,
            self.__on_write,
            self.__on_metadata
        )

        self.provider = provider
        self.address = address
        self.data = initialValue
        self.metadata = Variant()


        self.providerNode = datalayer.provider_node.ProviderNode(self.cbs)

    def register_node(self):
      self.provider.register_node(self.address, self.providerNode)

    def set_value(self,value: Variant):
        self.data = value

    def create_metadata(self,typeAddress = "none"):
        # Create metadata
        
        # Create `FlatBufferBuilder`instance. Initial Size 1024 bytes (grows automatically if needed)
        builder                    = flatbuffers.Builder(1024)

        # Serialize AllowedOperations data
        AllowedOperations.AllowedOperationsStart(builder)
        AllowedOperations.AllowedOperationsAddRead(builder, True)
        AllowedOperations.AllowedOperationsAddWrite(builder, True)
        AllowedOperations.AllowedOperationsAddCreate(builder, True)
        AllowedOperations.AllowedOperationsAddDelete(builder, False)
        operations = AllowedOperations.AllowedOperationsEnd(builder)

        # Metadata description strings
        descriptionBuilderString   = builder.CreateString("sample schema inertial value type")
        urlBuilderString           = builder.CreateString("tbd")

        # Metadata reference table only necessary for flatbuffers
        if self.data.get_type() == VariantType.FLATBUFFERS:
            # Store string parameter into builder
            readTypeBuilderString      = builder.CreateString("readType")
            writeTypeBuilderString     = builder.CreateString("writeType")
            createTypeBuilderString    = builder.CreateString("createType")
            targetAddressBuilderString = builder.CreateString(typeAddress)

            # Serialize Reference data (for read operation)
            Reference.ReferenceStart(builder)
            Reference.ReferenceAddType(builder, readTypeBuilderString)
            Reference.ReferenceAddTargetAddress(builder, targetAddressBuilderString)
            reference_read = Reference.ReferenceEnd(builder)

            # Serialize Reference data (for write operation)
            Reference.ReferenceStart(builder)
            Reference.ReferenceAddType(builder, writeTypeBuilderString)
            Reference.ReferenceAddTargetAddress(builder, targetAddressBuilderString)
            reference_write = Reference.ReferenceEnd(builder)

            # Serialize Reference data (for create operation)
            Reference.ReferenceStart(builder)
            Reference.ReferenceAddType(builder, createTypeBuilderString)
            Reference.ReferenceAddTargetAddress(builder, targetAddressBuilderString)
            reference_create = Reference.ReferenceEnd(builder)

            # Create FlatBuffer vector and prepend reference data. Note: Since we prepend the data, prepend them in reverse order.
            Metadata.MetadataStartReferencesVector(builder,3)
            builder.PrependSOffsetTRelative(reference_create)
            builder.PrependSOffsetTRelative(reference_write)
            builder.PrependSOffsetTRelative(reference_read)
            references = builder.EndVector(3)

                    

        # Serialize Metadata data
        Metadata.MetadataStart(builder)
        Metadata.MetadataAddOperations(builder,operations)
        Metadata.MetadataAddDescription(builder, descriptionBuilderString)
        Metadata.MetadataAddDescriptionUrl(builder, urlBuilderString)
        # Metadata reference table only necessary for flatbuffers
        if self.data.get_type() == VariantType.FLATBUFFERS:
            Metadata.MetadataAddReferences(builder, references)
        metadata = Metadata.MetadataEnd(builder)

        # Closing operation
        builder.Finish(metadata)
        result = self.metadata.set_flatbuffers(builder.Output())   
        if result != datalayer.variant.Result.OK:
            print("ERROR creating flatbuffers (metadata) failed with: ", result)
            return  

    def __on_create(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_create()", "address:", address, "userdata:", userdata)
        cb(Result.OK, data)

    def __on_remove(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_remove()", "address:", address, "userdata:", userdata)
        cb(Result.UNSUPPORTED, None)

    def __on_browse(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_browse()", "address:", address, "userdata:", userdata)
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result.OK, new_data)

    def __on_read(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_read()", "address:", address, "data:", self.data, "userdata:", userdata)
        new_data = self.data
        cb(Result.OK, new_data)

    def __on_write(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        _data = data
        print(data.get_string())
        if 'SNAP' in os.environ:
            conn = sqlite3.connect('/var/snap/rexroth-solutions/common/solutions/activeConfiguration/test.db')
        else:
            conn = sqlite3.connect('test.db')   
        conn.execute("pragma journal_mode=wal;")
        #c = conn.cursor
        try:
            completeScript = data.get_string()
            commandLength = len(completeScript)
            singleStatements = completeScript.split(";")
            #if the last character is ";" then we will run the entire thing as script
            if completeScript[-1] == ";":
                #queryresult = str(conn.executescript(completeScript).fetchmany(2000))
                queryresult = str(conn.executescript(completeScript).fetchall())
                conn.commit()
            #if the last character is not ; then run as a script except the last statement which will return a result    
            else:    
                singleStatements = completeScript.split(";")
                conn.executescript(completeScript[:-len(singleStatements[-1])])
                #for i in singleStatements:
                conn.commit()
                #queryresult = str(conn.execute(singleStatements[-1]).fetchmany(2000))
                cur = conn.cursor()
                #queryresult = str(cur.execute(singleStatements[-1]).fetchall())
                rv = cur.execute(singleStatements[-1]).fetchall()
                queryresult = str(rv)
                #test stuff
                
                #this can be used to return json
                #if cur.description is None:
                #    queryresult = str(rv)
                #else:    
                #    row_headers=[x[0] for x in cur.description] #this will extract row headers
                #    json_data=[]
                #    for result in rv:
                #        json_data.append(dict(zip(row_headers,result)))
                #    queryresult = json.dumps(json_data)
                conn.commit()
            print(queryresult)
            _data.set_string(queryresult)
        except Error as e:  
            print(e)
            _data.set_string("SQL error " + str(e))

        if conn: 
            conn.close()
        result, self.data = _data.clone()
        cb(Result.OK, self.data)

    def __on_metadata(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_metadata()", "address:", address,"metadata:",self.metadata, "userdata:", userdata)
        cb(Result.OK, self.metadata)

class ConfigurationNode:

    def __init__(self,provider : datalayer.provider, address : str , initialValue: Variant):

        self.cbs = ProviderNodeCallbacks(
            self.__on_create,
            self.__on_remove,
            self.__on_browse,
            self.__on_read,
            self.__on_write,
            self.__on_metadata
        )

        self.provider = provider
        self.address = address
        self.data = initialValue
        self.metadata = Variant()


        self.providerNode = datalayer.provider_node.ProviderNode(self.cbs)

    def register_node(self):
      self.provider.register_node(self.address, self.providerNode)

    def set_value(self,value: Variant):
        self.data = value

    def create_metadata(self,typeAddress = "none"):
        # Create metadata
        
        # Create `FlatBufferBuilder`instance. Initial Size 1024 bytes (grows automatically if needed)
        builder                    = flatbuffers.Builder(1024)

        # Serialize AllowedOperations data
        AllowedOperations.AllowedOperationsStart(builder)
        AllowedOperations.AllowedOperationsAddRead(builder, True)
        AllowedOperations.AllowedOperationsAddWrite(builder, True)
        AllowedOperations.AllowedOperationsAddCreate(builder, True)
        AllowedOperations.AllowedOperationsAddDelete(builder, False)
        operations = AllowedOperations.AllowedOperationsEnd(builder)

        # Metadata description strings
        descriptionBuilderString   = builder.CreateString("sample schema inertial value type")
        urlBuilderString           = builder.CreateString("tbd")

        # Metadata reference table only necessary for flatbuffers
        if self.data.get_type() == VariantType.FLATBUFFERS:
            # Store string parameter into builder
            readTypeBuilderString      = builder.CreateString("readType")
            writeTypeBuilderString     = builder.CreateString("writeType")
            createTypeBuilderString    = builder.CreateString("createType")
            targetAddressBuilderString = builder.CreateString(typeAddress)

            # Serialize Reference data (for read operation)
            Reference.ReferenceStart(builder)
            Reference.ReferenceAddType(builder, readTypeBuilderString)
            Reference.ReferenceAddTargetAddress(builder, targetAddressBuilderString)
            reference_read = Reference.ReferenceEnd(builder)

            # Serialize Reference data (for write operation)
            Reference.ReferenceStart(builder)
            Reference.ReferenceAddType(builder, writeTypeBuilderString)
            Reference.ReferenceAddTargetAddress(builder, targetAddressBuilderString)
            reference_write = Reference.ReferenceEnd(builder)

            # Serialize Reference data (for create operation)
            Reference.ReferenceStart(builder)
            Reference.ReferenceAddType(builder, createTypeBuilderString)
            Reference.ReferenceAddTargetAddress(builder, targetAddressBuilderString)
            reference_create = Reference.ReferenceEnd(builder)

            # Create FlatBuffer vector and prepend reference data. Note: Since we prepend the data, prepend them in reverse order.
            Metadata.MetadataStartReferencesVector(builder,3)
            builder.PrependSOffsetTRelative(reference_create)
            builder.PrependSOffsetTRelative(reference_write)
            builder.PrependSOffsetTRelative(reference_read)
            references = builder.EndVector(3)

                    

        # Serialize Metadata data
        Metadata.MetadataStart(builder)
        Metadata.MetadataAddOperations(builder,operations)
        Metadata.MetadataAddDescription(builder, descriptionBuilderString)
        Metadata.MetadataAddDescriptionUrl(builder, urlBuilderString)
        # Metadata reference table only necessary for flatbuffers
        if self.data.get_type() == VariantType.FLATBUFFERS:
            Metadata.MetadataAddReferences(builder, references)
        metadata = Metadata.MetadataEnd(builder)

        # Closing operation
        builder.Finish(metadata)
        result = self.metadata.set_flatbuffers(builder.Output())   
        if result != datalayer.variant.Result.OK:
            print("ERROR creating flatbuffers (metadata) failed with: ", result)
            return  

    def __on_create(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_create()", "address:", address, "userdata:", userdata)
        cb(Result.OK, data)

    def __on_remove(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_remove()", "address:", address, "userdata:", userdata)
        cb(Result.UNSUPPORTED, None)

    def __on_browse(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_browse()", "address:", address, "userdata:", userdata)
        new_data = Variant()
        new_data.set_array_string([])
        cb(Result.OK, new_data)

    def __on_read(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        print("__on_read()", "address:", address, "data:", self.data, "userdata:", userdata)
        new_data = self.data
        cb(Result.OK, new_data)

    def __on_write(self, userdata: datalayer.clib.userData_c_void_p, address: str, data: Variant, cb: NodeCallback):
        result, self.data = data.clone()
        cb(Result.OK, self.data)

    def __on_metadata(self, userdata: datalayer.clib.userData_c_void_p, address: str, cb: NodeCallback):
        print("__on_metadata()", "address:", address,"metadata:",self.metadata, "userdata:", userdata)
        cb(Result.OK, self.metadata)
