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
-- Table structure for table `tranche_loan`
--

DROP TABLE IF EXISTS `tranche_loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tranche_loan` (
  `loan_id` int NOT NULL AUTO_INCREMENT,
  `tranche_id` int NOT NULL,
  `label` varchar(64) NOT NULL,
  `loan_type` varchar(45) DEFAULT 'MORTGAGE',
  `lender` varchar(45) NOT NULL,
  `account` varchar(45) NOT NULL DEFAULT '0',
  `address` json DEFAULT NULL,
  `issue_date` datetime DEFAULT NULL,
  `dated_date` datetime DEFAULT NULL,
  `maturity_date` datetime DEFAULT NULL,
  `coupon` float DEFAULT '0',
  `daycount` varchar(24) DEFAULT '30/360',
  `original_amount` float DEFAULT '0',
  `max_loan_amount` double DEFAULT '0' COMMENT 'Maximum loan, or max construction loan amount',
  `current_amount` float DEFAULT '0',
  `payment_date` datetime DEFAULT NULL,
  `payment_amount` float DEFAULT '0',
  `principal_amount` float DEFAULT '0',
  `status` varchar(45) NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (`loan_id`),
  UNIQUE KEY `idLoan_UNIQUE` (`loan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tranche_loan`
--

LOCK TABLES `tranche_loan` WRITE;
/*!40000 ALTER TABLE `tranche_loan` DISABLE KEYS */;
/*!40000 ALTER TABLE `tranche_loan` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:32
