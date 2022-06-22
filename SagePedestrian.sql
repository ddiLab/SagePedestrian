CREATE TABLE Person(
   PERMAID       INTEGER    PRIMARY KEY,
   DAYID         INTEGER    NOT NULL,
   USECROSSWALK  BIT(1) DEFAULT 0,
   USEROAD       BIT(1) DEFAULT 0,
   NS            BIT(1),
   EW            BIT(1)
);


CREATE TABLE Frame(
   DATE      TIMESTAMP PRIMARY KEY,
   PATH      CHAR(128) NOT NULL,
   FRAMEID   INT NOT NULL
);


CREATE TABLE Coordinate(
   TOTAL    INTEGER PRIMARY KEY,
   PERMAID  INTEGER   NOT NULL,
   DATE     TIMESTAMP NOT NULL,
   XCOORD   INTEGER   DEFAULT 0,
   YCOORD   INTEGER   DEFAULT 0,
   FOREIGN KEY (DATE) REFERENCES Frame (DATE),
   FOREIGN KEY (PERMAID) REFERENCES Person (PERMAID)
);

CREATE TABLE Contains(
   PERMAID  INT                NOT NULL,
   DATE    TIMESTAMP     NOT NULL,
   PRIMARY KEY (PERMAID, DATE),
   FOREIGN KEY (PERMAID) REFERENCES Person (PERMAID),
   FOREIGN KEY (DATE) REFERENCES Frame (DATE)
);
