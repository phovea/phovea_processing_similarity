phovea_processing_similarity [![Phovea][phovea-image]][phovea-url] [![NPM version][npm-image]][npm-url] [![Build Status][travis-image]][travis-url] [![Dependency Status][daviddm-image]][daviddm-url]
=====================

[Processing queue](https://github.com/phovea/phovea_processing_queue) plugin to compute similarities for categorical data of matrices, tables, and stratifications.

API will be available at `SERVER:PORT/api/similarity/` e.g.:
```
http://localhost:9000/api/similarity/group/jaccard/?range=11
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
[npm-image]: https://badge.fury.io/js/phovea_processing_similarity.svg
[npm-url]: https://npmjs.org/package/phovea_processing_similarity
[travis-image]: https://travis-ci.org/phovea/phovea_processing_similarity.svg?branch=master
[travis-url]: https://travis-ci.org/phovea/phovea_processing_similarity
[daviddm-image]: https://david-dm.org/phovea/phovea_processing_similarity/status.svg
[daviddm-url]: https://david-dm.org/phovea/phovea_processing_similarity
