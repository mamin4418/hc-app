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
-- Table structure for table `tranche`
--

DROP TABLE IF EXISTS `tranche`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tranche` (
  `tranche_id` int NOT NULL AUTO_INCREMENT,
  `tranche_name` varchar(64) NOT NULL,
  `company_id` int NOT NULL,
  `purchase_date` datetime DEFAULT NULL,
  `purchase_price` float DEFAULT '0',
  `closing_cost` float NOT NULL DEFAULT '0',
  `total_cost` float DEFAULT NULL,
  `current_debt` float NOT NULL DEFAULT '0',
  `sell_date` datetime DEFAULT NULL,
  `sell_price` float NOT NULL DEFAULT '0',
  `sell_cost` float NOT NULL DEFAULT '0',
  `current_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `current_price` float NOT NULL DEFAULT '0',
  `tranche_type` varchar(24) DEFAULT NULL,
  `description` varchar(45) DEFAULT NULL,
  `notes` varchar(512) NOT NULL DEFAULT 'NA',
  `status` varchar(45) NOT NULL DEFAULT 'ACTIVE',
  `updatedby` varchar(45) NOT NULL DEFAULT 'NA',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tranche_id`),
  UNIQUE KEY `idTranche_UNIQUE` (`tranche_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tranche`
--

LOCK TABLES `tranche` WRITE;
/*!40000 ALTER TABLE `tranche` DISABLE KEYS */;
INSERT INTO `tranche` VALUES (1,'MVS - NATASHA 72 Unit',1,'2020-11-17 00:00:00',6382000,46857.9,6428860,0,'1969-12-30 00:00:00',0,0,'2022-06-29 00:00:00',7462000,'Multifamily','72 Units','48 Units on Moss View Street and 24 UNits at Natasha Ct','ACTIVE','NA','2023-05-05 18:07:46');
/*!40000 ALTER TABLE `tranche` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:22
