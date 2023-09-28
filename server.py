#  coding: utf-8 
import socketserver
import os


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        # Receive request and process data
        self.data = self.request.recv(1024).strip()

        # print("Got a request of: %s\n" % self.data)

        # convert bytes from the data received to a string object
        decoded_data = self.data.decode('utf-8')
        decoded_header = decoded_data.splitlines()[0].split(" ")
        requested_path = decoded_header[1]

        # if HTTP request is GET, continue
        # else, return 405 since code cannot handle any other request
        if not self.__is_get_request(decoded_header):
            self.send_response(405, requested_path)
            return

        # handle the HTTP request based on provided path
        self.handle_path(requested_path)

    def handle_path(self, url_path) -> None:
        path = "www" + url_path

        if self.__is_path_base_directory(path):
            path += "index.html"

        # handle if the path doesn't end in "/", and thus, location is moved permanently
        if self.__is_location_moved(path):
            self.send_response(301, path)
            return

        # handle if path does not exist and thus, it can't be found
        if (not self.__is_path_valid(path)) or self.__is_unsecure_directory(path):
            self.send_response(404, path)
            return

        # once it gets here, that means the path is valid
        self.send_response(200, path)

    def get_200_status_code_response(self, path) -> str:
        content_type = self.get_content_type(path)
        http_header = ("HTTP/1.1 200 OK\r\n{}\r\nConnection: close\r\n\r\n"
                       .format(content_type))

        with (open(path, "r") as data_file):
            content_body = data_file.read()

        return http_header + content_body


    def get_301_status_code_response(self, location) -> str:
        return "HTTP/1.1 301 Moved Permanently\r\nLocation: {0}\r\n\r\n".format(location)

    def get_404_status_code_response(self) -> str:
        http_header = ("HTTP/1.1 404 Not Found\r\n"
                       "Content-Type: text/html\r\n"
                       "Connection: close\r\n\r\n")
        body = ("<!DOCTYPE html>"
                "<head><meta charset='UTF-8'></head>"
                "<html><body><h1>404 Not Found</h1></body></html>\n")
        return http_header + body

    def get_405_status_code_response(self) -> str:
        http_header = ("HTTP/1.1 405 Method Not Allowed\r\n"
                       "Content-Type: text/html\r\n"
                       "Connection: close\r\n\r\n")
        body = ("<!DOCTYPE html>"
                "<head><meta charset='UTF-8'></head>"
                "<html><body><h1>405 Method Not Allowed</h1></body></html>\n")
        return http_header + body

    def get_content_type(self, path) -> str:
        content_type = "Content-Type: "

        if self.__is_html(path):
            content_type += "text/html"
        elif self.__is_css(path):
            content_type += "text/css"
        else:
            content_type += "text/plain"

        return content_type

    def __is_css(self, path) -> bool:
        return path.endswith(".css")

    def __is_get_request(self, decoded_header) -> bool:
        return decoded_header[0] == "GET"

    def __is_html(self, path) -> bool:
        return path.endswith(".html")

    def __is_location_moved(self, path) -> bool:
        return not path.endswith("/") and not self.__is_html(path) and not self.__is_css(path)

    def __is_path_base_directory(self, path) -> bool:
        return path[-1] == "/"

    def __is_path_valid(self, path) -> bool:
        return os.path.exists(path)

    def __is_unsecure_directory(self, path) -> bool:
        return ".." in path

    def send_response(self, status_code, path) -> None:
        response = ""

        if status_code == 405:
            response = self.get_405_status_code_response()
        elif status_code == 404:
            response = self.get_404_status_code_response()
        elif status_code == 301:
            response = self.get_301_status_code_response(path[3:] + "/")
        elif status_code == 200:
            response = self.get_200_status_code_response(path)

        self.request.sendall(bytearray(response, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
