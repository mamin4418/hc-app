-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: pm
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `report_columns`
--

DROP TABLE IF EXISTS `report_columns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_columns` (
  `report_id` int NOT NULL,
  `columns` int NOT NULL,
  `columns_order` float DEFAULT NULL,
  PRIMARY KEY (`report_id`,`columns`),
  CONSTRAINT `fk_rc` FOREIGN KEY (`report_id`) REFERENCES `report` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_columns`
--

LOCK TABLES `report_columns` WRITE;
/*!40000 ALTER TABLE `report_columns` DISABLE KEYS */;
INSERT INTO `report_columns` VALUES (1,99,100),(1,101,20),(1,201,95),(1,202,90),(1,203,50),(1,205,80),(1,206,30),(1,207,40),(1,208,70),(1,4100,1),(2,99,30),(2,101,2),(2,201,20),(2,202,16),(2,203,10),(2,205,7),(2,206,3),(2,207,5),(2,208,5.95),(2,4100,1),(2,4106,1.1),(2,4410,1.2),(2,4440,1.3),(2,4460,1.4),(2,4470,1.5),(2,6072,8.3),(2,6073,8.2),(2,6074,8.4),(2,6076,5.5),(2,6077,8.6),(2,6080,4.1),(2,6101,4.2),(2,6105,4.3),(2,6109,8.75),(2,6111,8.1),(2,6112,9.2),(2,6141,8.8),(2,6142,8.9),(2,6144,15.1),(2,6146,9),(2,6147,9.1),(2,6148,9.3),(2,6149,9),(2,6150,8.7),(2,6161,2.5),(2,6162,4.4),(2,6163,2.7),(2,6171,6.1),(2,6172,6.2),(2,6173,6.3),(2,6175,6.4),(2,6191,6.6),(2,6193,6.5),(2,6194,15.8),(2,6270,4.5),(2,6300,8.5),(2,7010,15.2),(2,7030,15.3),(2,7050,9.4),(2,7060,15.5),(2,7061,15.4),(2,7151,15.6),(2,7161,15.7);
/*!40000 ALTER TABLE `report_columns` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:21
