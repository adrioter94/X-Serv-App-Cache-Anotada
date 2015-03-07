#!/usr/bin/python

import webapp
import urllib


class Proxy(webapp.webApp):

    def __init__(self, hostname, port):
        self.cache = {}
        self.cab1 = {}
        self.cab2 = {}
        webapp.webApp.__init__(self, hostname, port)

    def saveCache(self, resource, url):
        self.cache[resource] = url
        print "-----"
        for resources in self.cache:
            print resources, self.cache[resources]
        print "-----"

    def parse(self, request):
        resource = request.split()[1]
        resources = resource.split("/")
        if len(resources) == 2:
            resource2 = resource.split("/")[1]  # pagina que se pide
            resource1 = ""                      # recurso reload, cabezeras...
        elif len(resources) == 3:
            resource1 = resource.split("/")[1]
            resource2 = resource.split("/")[2]
        else:
            resource1 = resource
            resource2 = ""
        cabezeras = request.split("\r", 1)[1]
        self.cab1[resource2] = cabezeras
        parsedRequest = (resource1, resource2)
        return parsedRequest

    def urlOriginal(self, url):
        html = "<p><a href=" + url + ">url original</a>"
        return html

    def urlReload(self, parsedRequest):
        html = "<p><a href=http://localhost:1234/reload/"\
               + parsedRequest[1] + ">Reload</a>"
        return html

    def urlCab1(self, parsedRequest):
        html = "<p><a href=http://localhost:1234/cab1/"\
               + parsedRequest[1] + ">cabezeras1</a>"
        return html

    def urlCab2(self, parsedRequest):
        html = "<p><a href=http://localhost:1234/cab2/" \
               + parsedRequest[1] + ">cabezeras2</a>"
        return html

    def parseContenido(self, contenido, url, parsedRequest):
        pos1 = contenido.find("<body")
        pos2 = contenido.find(">", pos1)
        html1 = contenido[:pos2+1]
        html2 = contenido[pos2+1:]
        html = html1 + self.urlOriginal(url) + self.urlReload(parsedRequest)
        + self.urlCab1(parsedRequest) + self.urlCab2(parsedRequest)
        + html2
        return html

    def process(self, parsedRequest):
        pagina = parsedRequest[1]
        recurso = parsedRequest[0]
        Success = False
        Busqueda = False
        for resources in self.cache:
            if resources == pagina:
                url = self.cache[pagina]
                Success = True
        if pagina == "":
            return("404 Not Found", "<html><body><h1>"
                   + "Error: no se a pedido ningun recurso"
                   + "</h1></body></html>")
        if recurso == "reload":
            try:
                urlObject = urllib.urlopen(url)
            except IOError:
                return("400 Error", "<html><body><h1>"
                       + "Error: nombre del servicio desconocido"
                       + "</h1></body></html>")
            content = urlObject.read()
            code = str(urlObject.getcode())
            html = self.parseContenido(content, url, parsedRequest)
            return(code, html)

        elif recurso == "cab1":
            if Success:
                for resources in self.cab1:
                    if resources == pagina:
                        cabezeras = self.cab1[resources]
                        Busqueda = True
                if Busqueda:
                    return ("200 OK", "<html><body><h1><font size=3>"
                            + cabezeras + "</font></h1></body></html>")
                else:
                    return ("404 Not Found",
                            "<html><body><h1>Error</h1></body></html>")
            else:
                return ("404 Not Found",
                        "<html><body><h1>Error</h1></body></html>")

        elif recurso == "cab2":
            if Success:
                for resources in self.cab2:
                    if resources == pagina:
                        cabezeras = self.cab2[resources]
                        Busqueda = True
                if Busqueda:
                    return ("200 OK", "<html><body><h1><font size=3>"
                            + cabezeras + "</font></h1></body></html>")
                else:
                    return ("404 Not Found",
                            "<html><body><h1>Error</h1></body></html>")
            else:
                return ("404 Not Found",
                        "<html><body><h1>Error</h1></body></html>")

        if not Success:
            url = "http://" + parsedRequest[1]
            self.saveCache(parsedRequest[1], url)
        try:
            urlObject = urllib.urlopen(url)
        except IOError:
            return("400 Error", "<html><body><h1>"
                   + "Error: nombre del servicio desconocido"
                   + "</h1></body></html>")
        content = urlObject.read()
        code = str(urlObject.getcode())
        cabezeras_Server = str(urlObject.info())
        self.cab2[pagina] = cabezeras_Server
        html = self.parseContenido(content, url, parsedRequest)
        return(code, html)

if __name__ == "__main__":
    test = Proxy("localhost", 1234)
