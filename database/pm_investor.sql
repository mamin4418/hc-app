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
-- Table structure for table `investor`
--

DROP TABLE IF EXISTS `investor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investor` (
  `investor_id` int NOT NULL AUTO_INCREMENT,
  `label` varchar(45) NOT NULL DEFAULT 'AHUSA',
  `name` varchar(128) NOT NULL,
  `legal_name` varchar(64) NOT NULL DEFAULT '',
  `address1` varchar(45) DEFAULT NULL,
  `address2` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `state` varchar(16) DEFAULT NULL,
  `zip` varchar(10) DEFAULT NULL,
  `phone` varchar(16) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `tax_id` varchar(12) DEFAULT NULL,
  `type` varchar(16) NOT NULL DEFAULT 'INDIVIDUAL',
  `status` varchar(16) NOT NULL DEFAULT 'ACTIVE',
  `account` varchar(45) DEFAULT NULL,
  `note` varchar(128) DEFAULT 'NA',
  `updatedby` varchar(45) NOT NULL DEFAULT 'NA',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`investor_id`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investor`
--

LOCK TABLES `investor` WRITE;
/*!40000 ALTER TABLE `investor` DISABLE KEYS */;
INSERT INTO `investor` VALUES (1,'BBOYZ','Ankit Patel (Andy)','Ankit Patel','56 Williams Rd',NULL,'abcd','MA','02067','111-41411','manoj@yaho1o.com',NULL,'INDIVIDUAL','ACTIVE',NULL,'NA','NA','2020-09-13 13:13:32');
/*!40000 ALTER TABLE `investor` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:27
