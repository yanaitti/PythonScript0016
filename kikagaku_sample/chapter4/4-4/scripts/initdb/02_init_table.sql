\c analysis

DROP TABLE IF EXISTS iris_input;
DROP TABLE IF EXISTS iris_cluster;

CREATE TABLE iris_input (
  id serial NOT NULL,
  data_version varchar(16) NOT NULL,
  sepal_length numeric NOT NULL,
  sepal_width numeric NOT NULL,
  petal_length numeric NOT NULL,
  petal_width numeric NOT NULL,
  create_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  primary key (id, data_version)
);

CREATE TABLE iris_cluster (
  id serial NOT NULL,
  data_version varchar(16) NOT NULL,
  cluster_id numeric NOT NULL,
  pca1 numeric NOT NULL,
  pca2 numeric NOT NULL,
  create_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  primary key (id, data_version)
);
