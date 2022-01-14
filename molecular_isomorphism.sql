-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le :  ven. 14 jan. 2022 à 17:40
-- Version du serveur :  5.7.24
-- Version de PHP :  7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `molecular_isomorphism`
--

-- --------------------------------------------------------

--
-- Structure de la table `lab`
--

DROP TABLE IF EXISTS `lab`;
CREATE TABLE IF NOT EXISTS `lab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_chebi` varchar(50) NOT NULL,
  `atom_id` int(11) NOT NULL,
  `index` int(11) NOT NULL,
  `ctype` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `lab`
--

INSERT INTO `lab` (`id`, `id_chebi`, `atom_id`, `index`, `ctype`) VALUES
(1, 'CHEBI:90', 0, 0, '0'),
(2, 'CHEBI:90', 1, 1, '0'),
(3, 'CHEBI:90', 2, 2, '0'),
(4, 'CHEBI:90', 3, 3, '0'),
(5, 'CHEBI:90', 4, 4, '0'),
(6, 'CHEBI:90', 5, 5, '0'),
(7, 'CHEBI:90', 6, 6, '0'),
(8, 'CHEBI:90', 7, 7, '0'),
(9, 'CHEBI:90', 8, 8, '0'),
(10, 'CHEBI:90', 10, 9, '0'),
(11, 'CHEBI:90', 11, 10, '0'),
(12, 'CHEBI:90', 12, 11, '0'),
(13, 'CHEBI:90', 13, 12, '0'),
(14, 'CHEBI:90', 14, 13, '0'),
(15, 'CHEBI:90', 15, 14, '0'),
(16, 'CHEBI:90', 9, 15, '0'),
(17, 'CHEBI:90', 16, 16, '0'),
(18, 'CHEBI:90', 17, 17, '0'),
(19, 'CHEBI:90', 18, 18, '0'),
(20, 'CHEBI:90', 19, 19, '0'),
(21, 'CHEBI:90', 20, 20, '0'),
(22, 'CHEBI:90', 21, 21, '1'),
(23, 'CHEBI:90', 22, 22, '1'),
(24, 'CHEBI:90', 23, 23, '1'),
(25, 'CHEBI:90', 24, 24, '1'),
(26, 'CHEBI:90', 25, 25, '1'),
(27, 'CHEBI:90', 26, 26, '1');

-- --------------------------------------------------------

--
-- Structure de la table `links`
--

DROP TABLE IF EXISTS `links`;
CREATE TABLE IF NOT EXISTS `links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_chebi` varchar(100) NOT NULL,
  `atom_from` int(11) NOT NULL,
  `atom_to` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `links`
--

INSERT INTO `links` (`id`, `id_chebi`, `atom_from`, `atom_to`, `version`) VALUES
(1, 'CHEBI:90', 3, 0, 0),
(2, 'CHEBI:90', 0, 20, 0),
(3, 'CHEBI:90', 0, 1, 0),
(4, 'CHEBI:90', 1, 2, 0),
(5, 'CHEBI:90', 2, 19, 0),
(6, 'CHEBI:90', 2, 5, 0),
(7, 'CHEBI:90', 4, 3, 0),
(8, 'CHEBI:90', 4, 9, 0),
(9, 'CHEBI:90', 4, 5, 0),
(10, 'CHEBI:90', 5, 6, 0),
(11, 'CHEBI:90', 6, 7, 0),
(12, 'CHEBI:90', 7, 18, 0),
(13, 'CHEBI:90', 7, 8, 0),
(14, 'CHEBI:90', 8, 9, 0),
(15, 'CHEBI:90', 8, 10, 0),
(16, 'CHEBI:90', 15, 10, 0),
(17, 'CHEBI:90', 10, 11, 0),
(18, 'CHEBI:90', 11, 12, 0),
(19, 'CHEBI:90', 12, 16, 0),
(20, 'CHEBI:90', 12, 13, 0),
(21, 'CHEBI:90', 13, 17, 0),
(22, 'CHEBI:90', 13, 14, 0),
(23, 'CHEBI:90', 14, 15, 0),
(24, 'CHEBI:90', 3, 0, 1),
(25, 'CHEBI:90', 0, 20, 1),
(26, 'CHEBI:90', 0, 1, 1),
(27, 'CHEBI:90', 1, 2, 1),
(28, 'CHEBI:90', 2, 19, 1),
(29, 'CHEBI:90', 2, 5, 1),
(30, 'CHEBI:90', 4, 3, 1),
(31, 'CHEBI:90', 4, 9, 1),
(32, 'CHEBI:90', 4, 5, 1),
(33, 'CHEBI:90', 5, 6, 1),
(34, 'CHEBI:90', 6, 7, 1),
(35, 'CHEBI:90', 7, 18, 1),
(36, 'CHEBI:90', 7, 8, 1),
(37, 'CHEBI:90', 8, 9, 1),
(38, 'CHEBI:90', 8, 10, 1),
(39, 'CHEBI:90', 15, 10, 1),
(40, 'CHEBI:90', 10, 11, 1),
(41, 'CHEBI:90', 11, 12, 1),
(42, 'CHEBI:90', 12, 16, 1),
(43, 'CHEBI:90', 12, 13, 1),
(44, 'CHEBI:90', 13, 17, 1),
(45, 'CHEBI:90', 13, 14, 1),
(46, 'CHEBI:90', 14, 15, 1),
(47, 'CHEBI:90', 0, 21, 1),
(48, 'CHEBI:90', 1, 21, 1),
(49, 'CHEBI:90', 2, 22, 1),
(50, 'CHEBI:90', 5, 22, 1),
(51, 'CHEBI:90', 4, 23, 1),
(52, 'CHEBI:90', 3, 23, 1),
(53, 'CHEBI:90', 10, 24, 1),
(54, 'CHEBI:90', 11, 24, 1),
(55, 'CHEBI:90', 12, 25, 1),
(56, 'CHEBI:90', 13, 25, 1),
(57, 'CHEBI:90', 14, 26, 1),
(58, 'CHEBI:90', 15, 26, 1);

-- --------------------------------------------------------

--
-- Structure de la table `molecules`
--

DROP TABLE IF EXISTS `molecules`;
CREATE TABLE IF NOT EXISTS `molecules` (
  `id_chebi` varchar(50) NOT NULL,
  `name` text NOT NULL,
  `formula` text NOT NULL,
  `dimension` varchar(10) NOT NULL,
  `family` text NOT NULL,
  `maximum_link` int(11) NOT NULL,
  `atoms_number` int(11) NOT NULL,
  `links_number` int(11) NOT NULL,
  `atoms` text NOT NULL,
  `links` text NOT NULL,
  `colored_atoms_number` int(11) DEFAULT NULL,
  `colored_links_number` int(11) DEFAULT NULL,
  `atoms_colored` text,
  `links_colored` text,
  `canonical_form1` text,
  `canonical_form2` text,
  `canonical_form3` text,
  PRIMARY KEY (`id_chebi`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `molecules`
--

INSERT INTO `molecules` (`id_chebi`, `name`, `formula`, `dimension`, `family`, `maximum_link`, `atoms_number`, `links_number`, `atoms`, `links`, `colored_atoms_number`, `colored_links_number`, `atoms_colored`, `links_colored`, `canonical_form1`, `canonical_form2`, `canonical_form3`) VALUES
('CHEBI:90', '(-)-epicatechin', 'C15H14O6', '2D', 'Alcohol', 2, 21, 23, 'C,0|C,1|C,2|C,3|C,4|C,5|C,6|C,7|C,8|C,10|C,11|C,12|C,13|C,14|C,15|O,9|O,16|O,17|O,18|O,19|O,20|', '3,0,1|0,20,1|0,1,2|1,2,1|2,19,1|2,5,2|4,3,2|4,9,1|4,5,1|5,6,1|6,7,1|7,18,1|7,8,1|8,9,1|8,10,1|15,10,1|10,11,2|11,12,1|12,16,1|12,13,2|13,17,1|13,14,1|14,15,2|', 27, 35, 'C,0,0|C,1,0|C,2,0|C,3,0|C,4,0|C,5,0|C,6,0|C,7,0|C,8,0|C,10,0|C,11,0|C,12,0|C,13,0|C,14,0|C,15,0|O,9,0|O,16,0|O,17,0|O,18,0|O,19,0|O,20,0|ZZZ,21,1|ZZZ,22,1|ZZZ,23,1|ZZZ,24,1|ZZZ,25,1|ZZZ,26,1|', '3,0,0|0,20,0|0,1,0|1,2,0|2,19,0|2,5,0|4,3,0|4,9,0|4,5,0|5,6,0|6,7,0|7,18,0|7,8,0|8,9,0|8,10,0|15,10,0|10,11,0|11,12,0|12,16,0|12,13,0|13,17,0|13,14,0|14,15,0|0,21,1|1,21,1|2,22,1|5,22,1|4,23,1|3,23,1|10,24,1|11,24,1|12,25,1|13,25,1|14,26,1|15,26,1|', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `ptn`
--

DROP TABLE IF EXISTS `ptn`;
CREATE TABLE IF NOT EXISTS `ptn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_chebi` varchar(50) NOT NULL,
  `ptn` text NOT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `ptn`
--

INSERT INTO `ptn` (`id`, `id_chebi`, `ptn`, `version`) VALUES
(1, 'CHEBI:90', '111111111111110111110111110', 0),
(2, 'CHEBI:90', '1111111111111111111110111110', 1);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
