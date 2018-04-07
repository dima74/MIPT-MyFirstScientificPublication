#pragma once

/*Модуль содержит описание структуры скелета в терминах классы-объекты.
  Этот модуль наследует многие вещи из модуля StructureTD, поскольку
  исторически был написан после него. Модуль StructureSkel описывает
  скелет как подмножество диаграммы Вороного, а модуль StructureTD
  описывает граф смежности сайтов - обобщённую триангуляцию Делоне,
  являющуюся двойственным графом для диаграммы Вороного*/

#include <QDebug>
#include <QPainter>
#include <ctime>
#include <set>
#include <fstream>
#include <sstream>
#include <cmath>
#include <vector>

#include "ContourTracer.h"
#include "LinkedList.h"
#include "SpanTree.h"
#include "StructureTD.h"
#include "TriDel.h"

using std::stringstream;
using std::ofstream;
using std::vector;
using std::sqrt;

struct ResultTable;
class TBone;
class TConnected;
class TNode;
class TPolFigure;
class Lacuna;

using uint = uint;

typedef Point TPoint;
typedef Element TSite;
typedef Vertex TVertex;
typedef Edge TEdge;

double sqr(double x);

/*Таблица для формирования статистики вычислений*/
struct ResultTable {
  int BMPm, BMPn; /* размеры образа строки - столбцы */
  int Polygons; /* количество полигональных контуров */
  int ConnectComp; /* количество связных копонент */
  int Points;      /* количество вершин в полигонах */
  int Vertex;      /* количество вершин в скелете */
  int Edges;       /* количество ребер в скелете */
  uint TimeTrace;    /* время трассировки */
  uint TimeTree;     /*Время построения дерева смежности контуров*/
  uint TimeSkelet;   /* время скелетизации */
  uint TimePrun;     /* время стрижки*/
  uint TimeSpectrum; /* время стрижки*/
  uint Total;        /* время общее*/

  ResultTable() = default;
};

enum NodeKind {
  Isolated, TailNode, JointNode, ForkNode
};
/*Возможные типы узла: изолированный, хвост, сустав,
  развилка - по числу выходящих костей 0,1,2,3 */

class TNode : public LinkedListElement<TNode> /*Элемент скелета типа 'узел'*/ {
  friend class TBone;
  friend class TConnected;
  friend class TPolFigure;

 public:
  int Number;      /*Порядковый номер*/
  TDisc* Disc;     /*Пустой круг узла*/
  TSite* Sites[3]; /*Массив инцидентных сайтов*/
  TBone* Bones[3]; /*массив инцидентных костей*/
  double Depth; /*глубина, используемая при стрижке*/
  TBone* Merge; /* Кость от присоединяемого штриха */
  double X();   //  координаты
  double Y();   //  узла
  double r();   //  и радиус его пустого круга
  NodeKind Kind(); /*определение типа узла*/
  
  TNode();
  virtual ~TNode();
  void AddBone(TBone* Bone);    /*добавить кость*/
  void DetachBone(TBone* Bone); /*отцепить кость*/
};

enum class BoneType {
  Linear,
  Parabolic,
  Hyperbolic,
};

class TBone : public LinkedListElement<TBone> /*Элемент скелета типа 'кость'*/ {
  friend class TConnected;
  friend class TNode;
  friend class TPolFigure;

 public:
  TConnected* Com; /*компонента, к которой относится кость*/
  TNode *org, *dest; /*Начальный и конечный узлы кости*/
  bool Met;          /* Метка */
  TPoint* Virt;      /*Контрольная точка для ребра-параболы, NIL для отрезка*/
  
  TBone();
  virtual ~TBone();
  void DestroyWithDetach(); /*отцепиться и уничтожить кость*/
  TNode* GetNextNode(TNode* Source);
  /*узел, противоположный Node на этой же кости*/
  void DetachNode(TNode* Node);
  /*отцепиться от узла*/
  void Bisector(TSite* E1, TSite* E2); /*Вычисление параболического бисектора*/
  void BezierPoints(double *X1, double *Y1, double *X2, double *Y2);
  /*Вычисление контрольных точек для параболического ребра*/
  bool Fiction(); /*кость вдоль фиктивного контура */

  double Length();
  TSite* Sites[2]; /* Образующие сайты */
  BoneType type;   /* Тип ребра */
  double t;        /* Длина проекции ребра на ось OX */
  double s;        /* Площадь собственной области */
  Lacuna* lacuna;  /* "Овраг, в который попадает отрезанная часть собственной
                      области */

  double p; /* Угол для линейного бицикла, фокальный параметр для
               параболического и расстояние между сайтами-точками для
               гиперболического */
  double x0;
  double y0;
  double dx;
  double dy;
  int dir; /* Направление поворота между осями OX и OY, 1 - против часовой
              стрелки, -1 - по часовой */

  void DetermineType(); /* Определить тип бицикла и пару инцидентных сайтов */
  QPair<QPointF, double> GetMinimum();
  /* Определить внутреннюю точку минимумa радиальной функции и значение в ней
     в том случае, если она существует*/
  void FillInfo(); /* Определить значения всех незаполненных полей */
  double Square(double r); /* Вычислить площадь открытия бицикла без
                              максимального круга */
  QPair<QPointF, bool> GetExtremePoint(double r);
  /* Определить крайнюю точку бицикла, если бицикл не исчез полностью */
  double SectorArea(double r); 
  /* Площадь внешнего сектора меньшего концевого круга */
};

class TConnected : public LinkedListElement<TConnected>
/*Связная компонента многоугольной фигуры */ {
  friend class TBone;
  friend class TNode;
  friend class TPolFigure;

 public:
  TContour* Border; /* Внешний контур компоненты */
  LinkedListTail<TNode>* Nodes; /* Список узлов скелета компоненты */
  LinkedListTail<TBone>* Bones; /* Список костей скелета компоненты */
  /* скелет компненты - только то, что лежит внутри нее */
  vector<TContour*> HoleList; /* Список дыр - внутренних контуров компоненты */
  void CutSkeleton(double Eps); /* стрижка-укорачивание на Eps - точность */
  TConnected();
  virtual ~TConnected();
};

class TPolFigure : public Domain
/*Граничное и скелетное представление бинарной области */
/*Описание скелета области в виде списков узлов и костей*/ {
  typedef Domain inherited;
  friend class TBone;
  friend class TConnected;
  friend class TNode;

 public:
  LinkedListTail<TConnected>* Components; /*Список компонент многоуг.фигуры*/
  bool SkelExist;    /*Признак, что скелет построен*/
  bool InternalSkel; /*Текущий скелет - внутрений*/
  ResultTable RTab;  /*Статистика вычислений*/
  virtual ~TPolFigure();
  TPolFigure(BitRaster* PM, double Amin);
  /*Построение компонент для битмапа с отбрасыванием малых контуров*/
  void CreateContours(ContourTracer* BinIm);
  /*Построение контуров для бинарного образа BinIm*/
  void MakeComponents();
  /*Формирование компонент из контуров*/
  void Invert();
  /*Инверсия фигуры*/
  void RestoreInversion();
  /*Восстановление фигуры после инверсии*/
  void ClearAll(); /*Чистка всех списков*/
  void MakeNodeBoneRepresentation();
  /*Построение скелета по графу смежности (трианг.Делоне)*/
  void MakeTriangDel(); /*Построение графа смежности*/
  void CutSkeleton(double Eps); /*Стрижка скелета с параметром Eps*/
  vector<double> GetBonesLengths() const;
  vector<double> GetContourAngles() const;
  vector<double> GetContourLengths() const;
  TPolFigure() {}

  void MonotonicSubdivision(); /*Разбиение на монотонные ребра*/
  list<TBone*> AllBones;
  list<Lacuna*> Lacunas;
};

class Lacuna {
 public:
  list<TBone*> Bones;
  list<TBone*> Truncated;
  list<QPair<TBone*, TBone*>> Pairs;
  QColor color;
  Lacuna();
  void AddBone(TBone* Bone, double rad);
  void Absorb(Lacuna* Inflow, double rad);
};

double PairSquare(TBone* BoneA, TBone* BoneB, double rad);
bool CheckPair(TBone* BoneA, TBone* BoneB, double rad);

uint TimeInMilSecond(); /*Текущее время в миллисекундах*/
extern int NodeCount, BoneCount, CompCount; /*Число узлов, костей и компонент*/
