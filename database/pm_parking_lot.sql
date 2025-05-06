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
-- Table structure for table `parking_lot`
--

DROP TABLE IF EXISTS `parking_lot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parking_lot` (
  `pl_id` int NOT NULL,
  `tranche_id` int NOT NULL DEFAULT '0',
  `group` varchar(64) DEFAULT NULL,
  `label` varchar(64) NOT NULL,
  `label2` varchar(128) DEFAULT NULL,
  `street` varchar(96) DEFAULT NULL,
  `unit` varchar(12) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `state` varchar(2) DEFAULT NULL,
  `zip` varchar(6) DEFAULT NULL,
  `parent` int DEFAULT NULL,
  `pl_status` varchar(45) DEFAULT NULL,
  `setup` double DEFAULT '0',
  `monthly` double DEFAULT '0',
  `parking_spots` int NOT NULL DEFAULT '1',
  `location` varchar(45) DEFAULT NULL,
  `description` varchar(512) DEFAULT NULL,
  `updatedby` varchar(45) NOT NULL DEFAULT 'INIT',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`pl_id`),
  KEY `p_label` (`label`,`city`,`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parking_lot`
--

LOCK TABLES `parking_lot` WRITE;
/*!40000 ALTER TABLE `parking_lot` DISABLE KEYS */;
INSERT INTO `parking_lot` VALUES (1,1,'MVS','240MVS','240 Moss View St','240 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(2,1,'MVS','246MVS','246 Moss View St','246 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(3,1,'MVS','252MVS','252 Moss View St','252 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(4,1,'MVS','258MVS','258 Moss View St','258 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(5,1,'MVS','300MVS','300 Moss View St','300 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(6,1,'MVS','306MVS','306 Moss View St','306 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(7,1,'SRD','5774NC-A','5774 Natasha Ct A','5774 Natasha Court A',NULL,'Bowling Green','KY','42104',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(8,1,'SRD','5790NC','5790 Natasha Ct','5790 Natasha Court',NULL,'Bowling Green','KY','42104',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(9,5,'JL','2463KENBALE','2463 Ken Bale Boulevard','2463 Ken Bale Boulevard',NULL,'Bowling Green','KY','42103',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(10,5,'NL','1260KENILWOOD','1260 Kenilwood Way','1260 Kenilwood Way',NULL,'Bowling Green','KY','42104',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(11,2,'MVS','222MVS','222 Moss View Street','222 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(12,2,'MVS','228MVS','228 Moss View Street','228 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(13,2,'MVS','234MVS','234 Moss View Street','234 Moss View Street',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(14,4,'WINDOVER','173WINDOVER','173 Windover Avenue','173 Windover Avenue',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(15,3,'TRADITIONS','TRADITIONS','Lovers Lane','Lovers Lane',NULL,'Bowling Green','KY','42103',0,'ACTIVE',0,0,60,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(16,6,'AUDLEY','110AUDLEY','110 Audley Ct','110 Audley Ct',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(17,7,'OTTE','5898OTTE','5898 Otte Ct','5898 Otte Ct',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(18,9,'US31BYPASS','1607US31','1607 US 31W Bypass','1607 US 31W Bypass',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,46,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(19,9,'US31BYPASS','1720US31','1720 US 31W Bypass','1720 US 31W Bypass',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,46,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(20,10,'GRANDEHEAVEN','2730ID','2730 Fitzerald Industrial Drive','2730 Fitzerald Industrial Drive',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(21,10,'GRANDEHEAVEN','2758ID','2758 Fitzerald Industrial Drive','2758 Fitzerald Industrial Drive',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(22,10,'GRANDEHEAVEN','2782ID','2782 Fitzerald Industrial Drive','2782 Fitzerald Industrial Drive',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(23,10,'GRANDEHEAVEN','2796ID','2796 Fitzerald Industrial Drive','2796 Fitzerald Industrial Drive',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(24,10,'GRANDEHEAVEN','503NRW','503 Nathans Rim Way','503 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(25,10,'GRANDEHEAVEN','515NRW','515 Nathans Rim Way','515 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(26,10,'GRANDEHEAVEN','527NRW','527 Nathans Rim Way','527 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(27,10,'GRANDEHEAVEN','539NRW','539 Nathans Rim Way','539 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(28,10,'GRANDEHEAVEN','504NRW','504 Nathans Rim Way','504 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(29,10,'GRANDEHEAVEN','2780ID','2870 Fitzerald Industrial Drive','2870 Fitzerald Industrial Drive',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(30,10,'GRANDEHEAVEN','518NRW','518 Nathans Rim Way','518 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(31,10,'GRANDEHEAVEN','532NRW','532 Nathans Rim Way','532 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02'),(32,10,'GRANDEHEAVEN','546NRW','546 Nathans Rim Way','546 Nathans Rim Way',NULL,'Bowling Green','KY','42101',0,'ACTIVE',0,0,16,'0','Private Parking Lot','PP','2022-12-05 15:58:02');
/*!40000 ALTER TABLE `parking_lot` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-21 17:18:20
