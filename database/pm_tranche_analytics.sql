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
-- Table structure for table `tranche_analytics`
--

DROP TABLE IF EXISTS `tranche_analytics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tranche_analytics` (
  `tranche_id` int NOT NULL,
  `tdate` datetime NOT NULL,
  `rr_units` float DEFAULT '0',
  `oc_units` float DEFAULT '0',
  `ot_units` float DEFAULT NULL,
  `expected_rent` float NOT NULL DEFAULT '0',
  `current_rent` float DEFAULT NULL,
  `paid_rent` float NOT NULL DEFAULT '0',
  `deliquency` float NOT NULL DEFAULT '0',
  `sd_r` float NOT NULL DEFAULT '0',
  `sd_a` float NOT NULL DEFAULT '0',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(45) NOT NULL DEFAULT 'NA',
  PRIMARY KEY (`tdate`,`tranche_id`),
  UNIQUE KEY `id_ta_UNIQUE` (`tranche_id`,`tdate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tranche_analytics`
--

LOCK TABLES `tranche_analytics` WRITE;
/*!40000 ALTER TABLE `tranche_analytics` DISABLE KEYS */;
/*!40000 ALTER TABLE `tranche_analytics` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:29
