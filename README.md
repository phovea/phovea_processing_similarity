phovea_processing_similarity
=====================
 [![Phovea][phovea-image]][phovea-url]  [![Build Status][circleci-image]][circleci-url] 
 
 

[Processing queue](https://github.com/phovea/phovea_processing_queue) plugin to compute similarities for categorical data of matrices, tables, and stratifications.

API will be available at `SERVER:PORT/api/similarity/` e.g.:
```
http://localhost:9000/api/similarity/group/jaccard/?range=(11,12,13)
```
You receive a UUID which is used to query the results (please note the different namespace) , e.g. with:
```
http://localhost:9000/api/processing/res/dff39dde-a787-40fb-a98a-8687f27e80c5
``` 
Please note the different namespace for result retrieval as this route is defined in the phovea_processing_queue plugin.
That also applies for the event stream:
```
http://localhost:9000/api/processing/stream
``` 

Installation
------------

```
git clone https://github.com/phovea/phovea_processing_similarity.git
cd phovea_processing_similarity
npm install
```

Testing
-------

```
npm test
```

Building
--------

```
npm run build
```



***

<a href="https://caleydo.org"><img src="http://caleydo.org/assets/images/logos/caleydo.svg" align="left" width="200px" hspace="10" vspace="6"></a>
This repository is part of **[Phovea](http://phovea.caleydo.org/)**, a platform for developing web-based visualization applications. For tutorials, API docs, and more information about the build and deployment process, see the [documentation page](http://phovea.caleydo.org).


[phovea-image]: https://img.shields.io/badge/Phovea-Server%20Plugin-10ACDF.svg
[phovea-url]: https://phovea.caleydo.org
[circleci-image]: https://circleci.com/gh/phovea/phovea_processing_similarity.svg?style=shield
[circleci-url]: https://circleci.com/gh/phovea/phovea_processing_similarity
