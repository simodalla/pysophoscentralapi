# PySophosCentralApi

This is both a library and an application that will need to work with the CLI for developers and data analysts.

## The problem

Interfacing with the rest APIs Sophos Central <https://developer.sophos.com/>, <https://developer.sophos.com/apis>, in order to interact, access, and interact with the data exposed by the specific [Endpoint APIs](https://developer.sophos.com/docs/endpoint-v1/1/overview) and [Common API](https://developer.sophos.com/docs/common-v1/1/overview)


## The solution

Questa libreria deve poter permettere di interrogare tutti gli endpoint e i vari metodi delle due api, Endpoint API e Common API e deve avere un’interfaccia cli per richiamare i vari enpoint.

Per tutti i metodi che permettono di leggere dati dalle api devono essere supportati i vari filtri di ricerca e la possibilità di esportare i dati estratti in file json e csv oltre che in output.

We want to be sure to employ color to communicate to our users. Feel free to 
include the colorma python package for this.
