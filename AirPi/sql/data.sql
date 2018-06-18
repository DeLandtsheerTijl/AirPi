CREATE TABLE `tbldata` (
   `iddata` int(11) NOT NULL AUTO_INCREMENT,
   `sensordata` decimal(10,2) NOT NULL,
   `timeofmeasurement` datetime NOT NULL,
   `sensorid` int(11) NOT NULL,
   PRIMARY KEY (`iddata`),
   KEY `sensorid_idx` (`sensorid`),
   CONSTRAINT `sensorid` FOREIGN KEY (`sensorid`) REFERENCES `tblsensor` (`idsensor`) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8