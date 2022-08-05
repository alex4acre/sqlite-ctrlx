# README sqlite-ctrlx

This python app __sqlite-ctrlx__ provides datalayer nodes on a bosch rexroth ctrlX core for interaction with an SQLite database residing on the core.

## Usage

Enter SQL commmands into the terminals provided on the ctlrX core datalayer at SQLite/teminal-x. Use a semicolon between commands to run multiple commands. 
The last command will return a result if reqested and not followed by a semicolon (a semicolon will suppress responses from the database).


### Commands can be given with the PUT REST Command. An example is shown here.

Here a table is created and the response is empty.

![image](https://user-images.githubusercontent.com/89591244/183098877-95282298-6fdb-478c-9d32-fe16f0ba7b78.png)



Here, a series of commands are issued with a semi-colon between each command.

![image](https://user-images.githubusercontent.com/89591244/183099242-34b6cc5a-9628-42e5-8b51-7e41d4f85c35.png)



Here, a set of data is pulled and the response shows the requested data.

![image](https://user-images.githubusercontent.com/89591244/183099326-3b06c7f7-9108-439d-bd87-60321c1bcaeb.png)



Here, more specific data is pulled form the table. 

![image](https://user-images.githubusercontent.com/89591244/183099430-86ee8857-babb-4ae8-acac-9be2e75c2d49.png)



### The database flies is stored in the app data of the ctrlX and can be downloaded or archived through the ctrlX utilites. 

![image](https://user-images.githubusercontent.com/89591244/182950447-2146e82b-c539-4843-b8c0-f3a72ab69b7d.png)



## License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
