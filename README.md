# README sqlite-ctrlx

This python app __sqlite-ctrlx__ provides datalayer nodes on a bosch rexroth ctrlX core for interaction with an SQLite database residing on the core.

## Usage

Enter SQL commmands into the terminals provided on the ctlrX core datalayer at SQLite/teminal-x. Use a semicolon between commands to run multiple commands. 
The last command will return a result if reqested and not followed by a semicolon (a semicolon will suppress responses from the database).

Commands can be given with the PUT REST Command. An example is shown here requesting data form the table. The response is below.

![image](https://user-images.githubusercontent.com/89591244/182952036-0b13fcbc-ab4e-4367-8544-b60706b5c9ae.png)


The database flies is stored in the app data of the ctrlX and can be downloaded or archived through the ctrlX utilites. 

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
