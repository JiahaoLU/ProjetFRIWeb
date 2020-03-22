# ProjetFRIWeb
Répertoire pour le projet et la restitution d'article du cours FRI-Web

## Contenu
* Veuillez utiliser `$ pip install -r requirements.txt` afin d'installer les packages nécessaires.
* **Sous 'Restitution_of_article'**:<br/> Implémentation simple du méthode de recherche rapide dans l'article "Faster and Smaller Inverted Indices with Treaps": https://drive.google.com/file/d/1TomasdiqWvl0NaHy9h2NzTncrE6LRM08/view?usp=sharing.
    * Construction de treap and compression de treap à un arbre général et à la présentation en parenthèses,
    * L'algorithme de recherche rapide de l'intersection et de l'union.
    * Implémentation sur les exemples triviaux

* **Sous 'Projet'**:<br/> Projet FRIWeb en utilisant de différents modèles.
    * Usage:<br/>
  1. Ouvrir le terminal et faire éxecuter `Main.py`
  2. Le programme se présente en tant qu'une application sur terminal, Voici l'instruction:<br/>
  **Attention: La colloection de Stanford cs276 est relativement volumineuse. Veuillez utiliser `--gi` avec précaution ! Sinon, sauter ce paramètre et utiliser l'index inversé déjà généré.**

  <pre>
  usage: Main.py [-h] --qm QM --rdir RDIR [--iidir IIDIR] [--cdir CDIR] [--gi]
               [--itype ITYPE] [--rmsw]

  -h, --help     show this help message and exit
  --qm QM        Choose the search module from: bool/vectorial/treap
  --rdir RDIR    Directory name where query results are saved.
  --iidir IIDIR  Folder name (where contains .ii files) where inverted index
                 are stored.
  --cdir CDIR    Directory name where the collection wished to be stored.
  --gi           True if generate new inverted index file from downloaded
                 collection.
  --itype ITYPE  Type of inverted index: doc/freq/pos
  --rmsw         True if stop words need to be removed.

  Quick start:
    $ python Main.py --qm vectorial --rdir results
  </pre>

  3. Attendre deux secondes pour le chargement de données. Une fois le programme se déroule, suivre les indications imprimées sous la ligne de commande. Un petit exemple:<br/>
    <pre>
    &lt&lt&ltDocQ research&gt&gt&gtPlease enter your keywords: computer students
    --- result in collection.cs276.nostp.freq.0.ii ---
    Local doc id = 3892, score = 1.00000
    Local doc id = 253, score = 1.00000
    Local doc id = 2954, score = 1.00000
    Local doc id = 2612, score = 1.00000
    ...
    Results saved in './results'.
    Continue? y/n
    </pre>

