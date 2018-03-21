#define _USE_MATH_DEFINES
#include <cmath>
#include <iostream>

#include "StructureSkel.h"

using std::isnan;
using std::min;
using std::cerr;
using std::endl;
using std::atan2;

using uint = uint;

double sqr(double x) {
  return x * x;
}

int NodeCount = 0, BoneCount = 0, CompCount = 0;

uint TimeInMilSecond()
/*Текущее время в миллисекундах*/
{
  return 1000 * (clock() / float(CLOCKS_PER_SEC));
}

double TNode::X() { return Disc->X; }

double TNode::Y() { return Disc->Y; }

double TNode::r() { return Disc->Rad; }

NodeKind TNode::Kind() {
  NodeKind result = NodeKind::Isolated;
  if (Bones[1 - 1] == nullptr) {
    result = NodeKind::Isolated;
  } else if (Bones[2 - 1] == nullptr) {
    result = NodeKind::TailNode;
  } else if (Bones[3 - 1] == nullptr) {
    result = NodeKind::JointNode;
  } else {
    result = NodeKind::ForkNode;
  }
  return result;
}

TConnected::TConnected()
    : Nodes(new LinkedListTail<TNode>), Bones(new LinkedListTail<TBone>) {
  CompCount++;
}

TNode::TNode() : Number(0), Disc(nullptr), Depth(0.0), Merge(nullptr) {
  for (int i = 0; i < 3; i++) {
    Bones[i] = nullptr;
    Sites[i] = nullptr;
  }
  ++NodeCount;
}

TNode::~TNode() {
  --NodeCount;
  delete Disc;
  // todo check:  inherited::Destroy;
}

void TNode::DetachBone(TBone* Bone) /*отцепить кость*/
{
  if (Bones[0] == Bone) {
    Bones[0] = Bones[1];
    Bones[1] = Bones[2];
    Bones[2] = nullptr;
  } else if (Bones[1] == Bone) {
    Bones[1] = Bones[2];
    Bones[2] = nullptr;
  } else if (Bones[2] == Bone)
    Bones[2] = nullptr;
}

TBone::TBone()
    : Com(nullptr), org(nullptr), dest(nullptr), Met(false), Virt(nullptr), lacuna(nullptr) {
  ++BoneCount;
}

TNode* TBone::GetNextNode(TNode* Source)
/*узел, противоположный Node на этой же кости*/
{
  if (org == Source) {
    return dest;
  } else if (dest == Source) {
    return org;
  } else {
    return nullptr;
  }
}

void TBone::DetachNode(TNode* Node) { /*отцепиться от узла*/
  if (Node == org) {
    org = nullptr;
  } else if (Node == dest) {
    dest = nullptr;
  } 
}

TBone::~TBone() {
  BoneCount--;
  if (Virt != nullptr) {
    delete Virt;
    Virt = nullptr;
  }
}

void TBone::DestroyWithDetach()
/*отцепиться и уничтожить кость*/
{
  if (org != nullptr) org->DetachBone(this);
  if (dest != nullptr) dest->DetachBone(this);
  BoneCount--;
  if (Virt != nullptr) {
    delete Virt;
    Virt = nullptr;
  }
  // todo check:  inherited::Destroy;
  // TODO find usage
}

bool TBone::Fiction()
/*кость вдоль фиктивного контура */
{
  bool result = false;
  bool b1 = false, b2 = false;
  b1 = false;
  b2 = false;
  for (int i = 1; i <= 3; i++) {
    b1 = b1 || org->Sites[i - 1]->Cont->Fiction;
    b2 = b2 || dest->Sites[i - 1]->Cont->Fiction;
  }
  result = b1 && b2;
  return result;
}

void TBone::Bisector(TSite* E1, TSite* E2)
/*Вычисление параболического бисектора*/
{
  double xv = 0.0, yv = 0.0, Z = 0.0;
  TPoint *s0 = nullptr, *S1 = nullptr, *S2 = nullptr, *St = nullptr;
  TDisc *C1 = nullptr, *C2 = nullptr, *ct = nullptr;
  double ex = 0.0, ey = 0.0, fx = 0.0, fy = 0.0;
  double d0 = 0.0, d1 = 0.0, d2 = 0.0, t0 = 0.0, t1 = 0.0, t2 = 0.0, a = 0.0,
         B = 0.0, M = 0.0, XT = 0.0, yt = 0.0;
  /*#
  St1:
  St2:
  St3:
  St4:
  St5:
  St6:
  St7:
  St8:
  */
  /*определение и правильная ориентация всех точек*/
  if (E1->IsVertex()) {
    s0 = ((Vertex*)E1)->p;
    S1 = ((TEdge*)E2)->org;
    S2 = ((TEdge*)E2)->dest;
  } else {
    s0 = ((Vertex*)E2)->p;
    S1 = ((TEdge*)E1)->org;
    S2 = ((TEdge*)E1)->dest;
  }
  Z = (S1->X - s0->X) * (S2->Y - s0->Y) - (S2->X - s0->X) * (S1->Y - s0->Y);
  if (Z == 0) return;
  if (Z < 0) {
    St = S1;
    S1 = S2;
    S2 = St;
  }
  C1 = org->Disc;
  C2 = dest->Disc;
  Z = (S2->X - S1->X) * (C2->X - C1->X) + (S2->Y - S1->Y) * (C2->Y - C1->Y);
  if (Z < 0) {
    ct = C1;
    C1 = C2;
    C2 = ct;
  }
  /*вычисление контрольной точки*/
  // St1:
  ex = S2->X - S1->X;
  ey = S2->Y - S1->Y;
  fx = -ey;
  fy = ex;
  // St2:
  M = Sqr(ex) + Sqr(ey);
  d1 = (ex * (C1->Y - S1->Y) - ey * (C1->X - S1->X)) / M;
  d2 = (ex * (C2->Y - S1->Y) - ey * (C2->X - S1->X)) / M;
  d0 = (ex * (s0->Y - S1->Y) - ey * (s0->X - S1->X)) / M;
  // St3:
  t1 = (ex * (C1->X - S1->X) + ey * (C1->Y - S1->Y)) / M;
  t2 = (ex * (C2->X - S1->X) + ey * (C2->Y - S1->Y)) / M;
  t0 = (ex * (s0->X - S1->X) + ey * (s0->Y - S1->Y)) / M;
  if (abs(t1 - t2) < 0.0001) return;
  // St4:
  B = d0 / 2;
  // St5:
  if (abs(t1 - t0) > abs(t2 - t0))
    a = (d1 - B) / Sqr(t1 - t0);
  else
    a = (d2 - B) / Sqr(t2 - t0);
  // St6:
  XT = ((t2 - t0) * t2 - (t1 - t0) * t1 - (d2 - d1) / (2 * a)) / (t2 - t1);
  yt = d1 + (XT - t1) * 2 * a * (t1 - t0);
  // St7:
  xv = S1->X + XT * ex + yt * fx;
  yv = S1->Y + XT * ey + yt * fy;
  Virt = new TPoint(xv, yv);
}

void TBone::BezierPoints(double *X1, double *Y1, double *X2, double *Y2)
/*Вычисление контрольных точек для параболического ребра*/
{
  if (Virt == nullptr) {
    *X1 = org->X();
    *Y1 = org->Y();
    *X2 = dest->X();
    *Y2 = dest->Y();
  } else {
    *X1 = org->X() + 2.0 * (Virt->X - org->X()) / 3;
    *Y1 = org->Y() + 2.0 * (Virt->Y - org->Y()) / 3;
    *X2 = dest->X() + 2.0 * (Virt->X - dest->X()) / 3;
    *Y2 = dest->Y() + 2.0 * (Virt->Y - dest->Y()) / 3;
    //       x1:=Virt.X; y1:=Virt.Y;
    //       x2:=Virt.X; y2:=Virt.Y;
  }
}

double TBone::Length() {
  return sqrt(sqr(org->X() - dest->X()) +
      sqr(org->Y() - dest->Y()));
}

TConnected::~TConnected()
/*Уничтожение компоненты*/
{
  TBone* B = nullptr;
  TNode* n = nullptr;
  HoleList.clear();
  while (!Bones->isEmpty()) {
    B = (TBone*)Bones->first();
    B->removeFromCurrentList();
    delete B;
  }
  while (!Nodes->isEmpty()) {
    n = (TNode*)Nodes->first();
    n->removeFromCurrentList();
    delete n;
  }
  delete Bones;
  delete Nodes;
  CompCount--;
  // todo check:  inherited::Destroy;
}

void TConnected::CutSkeleton(double Eps)
/*стрижка-укорачивание на Eps - точность*/
{
  LinkedListTail<TNode>* Hairs;
  TNode *Node = nullptr, *Node1 = nullptr, *t = nullptr;
  TBone* Bone = nullptr;
  double l = 0.0, D = 0.0;
  /*поиск всех терминальных узлов*/
  Hairs = new LinkedListTail<TNode>;
  Node = (TNode*)Nodes->first();
  while (Node != nullptr) {
    Node1 = Node->getNext();
    Node->Depth = Node->r();
    if (Node->Kind() == NodeKind::TailNode) {
      Node->moveIntoTail(Hairs);
    }
    Node = Node1;
  }
  /*собственно стрижка*/
  while (!Hairs->isEmpty()) {
    t = (TNode*)Hairs->first();
    Bone = t->Bones[0];
    if (Bone != nullptr) {
      Node = Bone->GetNextNode(t);
      l = sqrt(Sqr(t->X() - Node->X()) + Sqr(t->Y() - Node->Y()));
      if ((l + t->Depth - Node->r() < Eps) && (Node->Kind() != NodeKind::TailNode)) {
        D = l + t->Depth;
        if (D > Node->Depth) {
          Node->Depth = D;
        }
        t->DetachBone(Bone);
        Bone->DetachNode(t);
        delete t;
        Bone->DetachNode(Node);
        Node->DetachBone(Bone);
        Bone->DestroyWithDetach();  /// !!!
        delete Bone;
        if (Node->Kind() == NodeKind::TailNode) {
          Node->moveIntoTail(Hairs);
        } 

      } else {
        t->moveIntoTail(Nodes);
      } 
    } else {
      delete t;
    } 
  }
  delete Hairs;
}

void TPolFigure::ClearAll() {
  TConnected* Com = nullptr; /*уничтожение компонент*/
  while (!Components->isEmpty()) {
    Com = (TConnected*)Components->first();
    delete Com;
  }
}

TPolFigure::~TPolFigure() {
  ClearAll();
  delete Components;
  Components = nullptr;
  // todo check:  inherited::Destroy;
}

TPolFigure::TPolFigure(BitRaster* bitRaster, double Amin)
/*Построение компонент для матрицы с отбрасыванием малых контуров*/
{
  uint TT, TT1;
  TT1 = TimeInMilSecond();
  Components = new LinkedListTail<TConnected>; /*Порождение списка компонент*/

  ContourTracer* BinIm = new ContourTracer(bitRaster, Amin);
  BinIm->traceContours();

  CreateContours(BinIm);
  /*Упорядочение контуров АВЛ деревом*/
  if (!ElementsExist) {
    ProduceElements(this);
    ElementsExist = true;
  }
  TT = TimeInMilSecond();
  SpaningTree(this);
  MakeComponents();

  RTab.TimeTree = TimeInMilSecond() - TT;
  RTab.ConnectComp = CompCount;
  delete BinIm;
  RTab.TimeTrace = TimeInMilSecond() - TT1 - RTab.TimeTree;
  RTab.Total = RTab.TimeTrace + RTab.TimeTree + RTab.TimeSkelet + RTab.TimePrun;
}

void TPolFigure::CreateContours(ContourTracer* BinIm)
/*Построение контуров для бинарного образа BinIm*/
{
  ClosedPath* CP; /* контур из растрового образа (модуль Kontur) */
  RasterPoint* r; /* точка контура (модуль Kontur) */
  TContour* S; /* контур для скелетизации (модуль Structure) */
  int i = 0;
  RTab.Points = 0;
  RTab.Polygons = 0;
  CP = BinIm->initialContour();
  while (CP != nullptr) {
    S = AddContour();
    S->Internal = CP->Internal;
    r = CP->initialPoint();
    i = 0;
    while (r != nullptr) {
      S->AddPoint(r->x, r->y);
      i++;
      r = r->getNext();
    }
    if (i < 3)
      delete S;
    else {
      S->ShiftHead();
      if (S->Internal == S->ConterClockWise()) S->Invert();
      S->ClosedPath = true;
      RTab.Polygons++;
      RTab.Points = RTab.Points + S->ListPoints->cardinal();
    }
    CP = CP->getNext();
  }
}

void TPolFigure::MakeComponents()
/*Формирование компонент из контуров*/
{
  TContour *S = nullptr, *S1 = nullptr, *S2 = nullptr;
  TConnected* Com = nullptr;
  /*Временное размещение внутренних контуров во внешние*/
  S = (TContour*)Boundary->first();
  while (S != nullptr) {
    S1 = S->getNext();
    if (S->Internal) {
      S2 = S->Container;
      if (S2->MySons == nullptr) S2->MySons = new LinkedListTail<TContour>;
      S->moveIntoTail(S2->MySons);
    }
    S = S1;
  }
  /*Из каждого внешнего создается компонента*/
  S = (TContour*)Boundary->first();
  while (S != nullptr) {
    if (!S->Internal) {
      Com = new TConnected;
      Com->Border = S;
      Com->moveIntoTail(Components);
      while (S->MySons != nullptr) {
        while (!S->MySons->isEmpty()) {
          S1 = (TContour*)S->MySons->first();
          Com->HoleList.push_back(S1);
          S1->moveIntoTail(Boundary);
        }
        delete S->MySons;
        S->MySons = nullptr;
      }
    }
    S = S->getNext();
  }
}

void TPolFigure::Invert() /*Инверсия фигуры*/
{
  TContour* S = nullptr;
  Point* p = nullptr;
  double xmin = 0.0, Xmax = 0.0, ymin = 0.0, Ymax = 0.0;
  int W = 0;
  W = 100;
  ClearAll();
  xmin = 10000;
  Xmax = -10000;
  ymin = 10000;
  Ymax = -10000;
  S = (TContour*)Boundary->first();
  while (S != nullptr) {
    S->Internal = !S->Internal;
    p = (Point*)S->ListPoints->first();
    while (p != nullptr) {
      if (p->X < xmin) xmin = p->X;
      if (p->X > Xmax) Xmax = p->X;
      if (p->Y < ymin) ymin = p->Y;
      if (p->Y > Ymax) Ymax = p->Y;
      p = p->getNext();
    }
    S->Invert();
    S->Container = nullptr;
    S->ClosestSite = nullptr;
    if (S->MySons != nullptr) delete S->MySons;
    S->MySons = nullptr;
    S = S->getNext();
  }
  S = new TContour;
  S->Internal = false;
  p = new Point(xmin - W, ymin - W);
  p->moveIntoTail(S->ListPoints);
  p = new Point(Xmax + W, ymin - W);
  p->moveIntoTail(S->ListPoints);
  p = new Point(Xmax + W, Ymax + W);
  p->moveIntoTail(S->ListPoints);
  p = new Point(xmin - W, Ymax + W);
  p->moveIntoTail(S->ListPoints);
  S->moveIntoTail(Boundary);
  S->Fiction = true;
  S->ShiftHead();
  if (S->Internal == S->ConterClockWise()) S->Invert();
  ElementsExist = false;
  ProduceElements(this);
  ElementsExist = true;
}

void TPolFigure::RestoreInversion()
/*Восстановление фигуры после инверсии*/
{
  TContour *S = nullptr, *s0 = nullptr;
  /*Удаление частей скелета, инцидентных фиктивному контуру*/
  ClearAll();
  SkelExist = false;
  /*  Com:=Components.first AS TConnected;
    WHILE Com<>NIL DO
    BEGIN
    Bone:=Com.Bones.first AS TBone;
    WHILE Bone<>NIL DO
    BEGIN
    Node:=Bone.Org;
    Node1:=Bone.Dest;
    Bone1:=Bone.suc AS TBone;
    IF Bone.Fiction THEN (*ребро инцидентное фиктивному контуру*)
    BEGIN
    Bone.DestroyWithDetach;
    IF Node.Kind=Isolated THEN Node.Destroy;
    IF Node1.Kind=Isolated THEN Node1.Destroy;
    END;
    Bone:=Bone1;
    END;
    Com:=Com.suc AS TConnected;
    END; */
  /*Инвертирование направления контуров*/
  S = (TContour*)Boundary->first();
  while (S != nullptr) {
    S->Internal = !S->Internal;
    if (S->Fiction)
      s0 = S;
    else {
      S->Invert();
      S->Container = nullptr;
      S->ClosestSite = nullptr;
    }
    S = S->getNext();
  }
  delete s0;
}

void printNode(TNode* n) {
  qDebug() << n->Disc->X << " " << n->Disc->Y << " " << n->Disc->Rad << endl;
}

void TPolFigure::MakeNodeBoneRepresentation()
/* Формирование структуры типа TPolFigure, описывающей
границу и внутренний скелет бинарной области из триангуляции.
Сама триангуляция при этом разрушается*/
{
  vector<Triplet*> ListOld;
  vector<TNode*> ListNew; /*Рабочие списки*/
  int M = 0;
  TNode *Node = nullptr, *Node1 = nullptr;
  TSite *S1 = nullptr, *S2 = nullptr;
  Triplet *Tr = nullptr, *Tr1 = nullptr;
  TBone* Bone = nullptr;
  TConnected* Com = nullptr;
  if ((Boundary == nullptr) || Boundary->isEmpty()) return;
  Com = (TConnected*)Components->first();
  while (Com != nullptr) {
    Tr = (Triplet*)Com->Border->Map->MapTriplet->first();
    M = 0;
    while (Tr != nullptr) {
      Node = new TNode;
      Node->Sites[1 - 1] = Tr->E1;
      Node->Sites[2 - 1] = Tr->E2;
      Node->Sites[3 - 1] = Tr->e3;
      Node->Disc = Tr->Circ;
      Tr->Circ = nullptr;
      M++;
      Tr->Numb = M;
      ListOld.push_back(Tr);
      ListNew.push_back(Node);
      Node->moveIntoTail(Com->Nodes); /* В список узлов */
      Tr = Tr->getNext();
      // printNode(Node);
    }
    /* M - число узлов*/

    /*Образование костей*/
    for (int stop = M - 1, i = 0; i <= stop; i++) {
      Tr = ListOld[i];
      Node = ListNew[i];
      for (int stop = 3, j = 1; j <= stop; j++) {
        switch (j) {
          case 1: {
            Tr1 = Tr->t1;
            S1 = Tr->e3;
            S2 = Tr->E1;
          } break;
          case 2: {
            Tr1 = Tr->t2;
            S1 = Tr->E1;
            S2 = Tr->E2;
          } break;
          case 3: {
            Tr1 = Tr->t3;
            S1 = Tr->E2;
            S2 = Tr->e3;
          } break;
          default:
            Tr1 = nullptr;
        }
        if ((Tr1 != nullptr) && (Tr->Numb < Tr1->Numb)) {
          Node1 = ListNew[Tr1->Numb - 1];
          Bone = new TBone;
          Bone->org = Node;
          Bone->dest = Node1;
          if (S1->IsVertex() == !S2->IsVertex())
            Bone->Bisector(S1, S2); /*параболическое ребро*/
          Bone->moveIntoTail(Com->Bones); /*В список костей*/
          Node->AddBone(Bone);
          Node1->AddBone(Bone);
        }
      }
    }
    ListOld.clear();
    ListNew.clear();
    delete Com->Border->Map;
    Com->Border->Map = nullptr;
    Com = Com->getNext();
  }
  SkelExist = true;
  ListOld.clear();
  ListNew.clear();
  RTab.Vertex = NodeCount;
  RTab.Edges = BoneCount;
}

void TPolFigure::MakeTriangDel() {
  uint TT = 0;
  TT = TimeInMilSecond();
  if (!ElementsExist) {
    ProduceElements(this);
    ElementsExist = true;
  }
  CreateTriangulation(this);
  MakeNodeBoneRepresentation();
  MapExist = true;
  RTab.TimeSkelet = TimeInMilSecond() - TT;
  RTab.Total = RTab.TimeTrace + RTab.TimeTree + RTab.TimeSkelet + RTab.TimePrun;
}

void TPolFigure::CutSkeleton(double Eps)
/*Стрижка скелета*/
{
  TConnected* Com = nullptr;
  uint TT = 0;
  TT = TimeInMilSecond();
  Com = (TConnected*)Components->first();
  while (Com != nullptr) {
    Com->CutSkeleton(Eps);
    Com = Com->getNext();
  }
  RTab.TimePrun = TimeInMilSecond() - TT;
  RTab.Vertex = NodeCount;
  RTab.Edges = BoneCount;
}

vector<double> TPolFigure::GetBonesLengths() const {
  vector<double> bones_lengths;
  auto comp = Components->first();
  while (comp != nullptr) {
    auto bone = comp->Bones->first();
    while (bone != nullptr) {
      bones_lengths.push_back(bone->Length());  bone = bone->getNext();
    }
    comp = comp->getNext();
  }
  return bones_lengths;
}

double CalculateAngle(const Point *point1, const Point *point2) {
  double vec_x = point2->X - point1->X;
  double vec_y = point2->Y - point1->Y;
  double angle = atan2(vec_y, vec_x);
  if (angle < 0) {
    angle += M_PI;
  }
  return angle;
}

double CalculateLength(const Point *point1, const Point *point2) {
  double vec_x = point2->X - point1->X;
  double vec_y = point2->Y - point1->Y;
  return sqrt(sqr(vec_y) + sqr(vec_x));
}

vector<double> TPolFigure::GetContourAngles() const {
  vector<double> contour_angels;
  auto comp = Components->first();
  while (comp != nullptr) {
    auto border = comp->Border;
    auto first_point = border->ListPoints->first();
    auto cur_point = first_point;
    auto next_point = first_point->getNext();
    while (next_point != nullptr) {
      contour_angels.push_back(CalculateAngle(cur_point, next_point));
      cur_point = next_point;
      next_point = next_point->getNext();
    }
    contour_angels.push_back(CalculateAngle(cur_point, first_point));
    comp = comp->getNext();
    contour_angels.push_back(-1543);
  }
  return contour_angels;
}

vector<double> TPolFigure::GetContourLengths() const {
  vector<double> contour_lengths;
  auto comp = Components->first();
  while (comp != nullptr) {
    auto border = comp->Border;
    auto first_point = border->ListPoints->first();
    auto cur_point = first_point;
    auto next_point = first_point->getNext();
    while (next_point != nullptr) {
      contour_lengths.push_back(CalculateLength(cur_point, next_point));
      cur_point = next_point;
      next_point = next_point->getNext();
    }
    contour_lengths.push_back(CalculateLength(cur_point, first_point));
    comp = comp->getNext();
    contour_lengths.push_back(-1543);
  }
  return contour_lengths;
}

void TNode::AddBone(TBone* Bone) /*добавить кость*/
{
  if (Bones[1 - 1] == nullptr)
    Bones[1 - 1] = Bone;
  else if (Bones[2 - 1] == nullptr)
    Bones[2 - 1] = Bone;
  else if (Bones[3 - 1] == nullptr)
    Bones[3 - 1] = Bone;
}

void TPolFigure::MonotonicSubdivision() {
  // Сделать подразбиение на монотонные рёбра
  TConnected* iComp = Components->first();
  while (iComp != nullptr) {
    list<TBone*> Skewed;
    TBone* iBone = iComp->Bones->first();
    while (iBone != nullptr) {
      iBone->DetermineType();
      if (iBone->type == BoneType::Parabolic || iBone->type == BoneType::Hyperbolic) {
        QPair<QPointF, double> MinPoint = iBone->GetMinimum();
        if (MinPoint.second >= 0) {
          // Бицикл содержит точку минимума
          if (MinPoint.second > iBone->org->r())
            MinPoint.second = iBone->org->r();
          if (MinPoint.second > iBone->dest->r())
            MinPoint.second = iBone->dest->r();
          TBone* nBone = new TBone(*iBone);  // Создаём новое ребро
          TNode* nNode =
              new TNode(*iBone->org);  // Создаём новый узел в точке минимума
          nNode->Disc = new TDisc(MinPoint.first.x(), MinPoint.first.y(),
                                  MinPoint.second);
          nNode->Bones[0] = iBone;
          nNode->Bones[1] = nBone;
          nNode->Bones[2] = nullptr;
          iBone->dest = iBone->org;
          iBone->org = nNode;
          nBone->org = nNode;
          bool stop = false;
          for (int i = 0; i < 3 && !stop; i++) {
            if (nBone->dest->Bones[i] == iBone) {
              nBone->dest->Bones[i] = nBone;
              stop = true;
            }
          }
          nBone->FillInfo();
          AllBones.push_back(nBone);
        }
      }
      iBone->FillInfo();
      AllBones.push_back(iBone);
      if (iBone->org->X() == iBone->dest->X() &&
          iBone->org->Y() == iBone->dest->Y() &&
          iBone->org->r() != iBone->dest->r()) {
        iBone->org->Disc->Rad = iBone->dest->r();
        Skewed.push_back(iBone);
      }
      iBone = iBone->getNext();
    }
    bool repeat = true;
    while (repeat) {
      repeat = false;
      for (auto iBone = Skewed.begin(); iBone != Skewed.end(); iBone++) {
        if ((*iBone)->org->X() == (*iBone)->dest->X() &&
            (*iBone)->org->Y() == (*iBone)->dest->Y() &&
            (*iBone)->org->r() != (*iBone)->dest->r()) {
          (*iBone)->org->Disc->Rad = (*iBone)->dest->r();
          repeat = true;
        }
      }
    }
    iComp = iComp->getNext();
  }
}

void TBone::DetermineType() {
  int found = 0;
  for (int i = 0; (i < 3) && (found < 2); i++) {
    for (int j = 0; (j < 3) && (found < 2); j++) {
      if (org->Sites[i] == dest->Sites[j]) {
        Sites[found++] = org->Sites[i];
      }
    }
  }
  if (!Sites[0]->IsVertex() && !Sites[1]->IsVertex())
    type = BoneType::Linear;
  else if (Sites[0]->IsVertex() && Sites[1]->IsVertex())
    type = BoneType::Hyperbolic;
  else
    type = BoneType::Parabolic;
}

QPair<QPointF, double> TBone::GetMinimum() {
  if (type == BoneType::Linear) {
    return (QPair<QPointF, double>(QPointF(0, 0), -1));
    // Точка минимума линейного ребра не является внутренней
  } else {
    double r = org->r();
    double R = dest->r();
    if (r > R) {
      double temp = r;
      r = R;
      R = temp;
    }
    // double l = sqrt((dest->X() - org->X()) * (dest->X() - org->X()) +
    //(dest->Y() - org->Y()) * (dest->Y() - org->Y()));
    if (type == BoneType::Parabolic) {
      if (!Sites[0]->IsVertex()) {
        // Сайт-точка будет всегда идти первым
        TSite* temp = Sites[0];
        Sites[0] = Sites[1];
        Sites[1] = temp;
      }
      double x1 = ((TVertex*)Sites[0])->p->X;
      double y1 = ((TVertex*)Sites[0])->p->Y;
      double x2 = ((TEdge*)Sites[1])->org->X;
      double y2 = ((TEdge*)Sites[1])->org->Y;
      double x3 = ((TEdge*)Sites[1])->dest->X;
      double y3 = ((TEdge*)Sites[1])->dest->Y;
      double rate = ((x1 - x2) * (x3 - x2) + (y1 - y2) * (y3 - y2)) /
                    ((x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2));
      // Отношение длины проекции к длине сайта-сегмента
      double x4 = x2 + rate * (x3 - x2);
      double y4 = y2 + rate * (y3 - y2);

      double cOrg = (org->X() - x1) * (y4 - y1) - (org->Y() - y1) * (x4 - x1);
      double cDest =
          (dest->X() - x1) * (y4 - y1) - (dest->Y() - y1) * (x4 - x1);
      if (cOrg * cDest < 0) {
        // Точки по разные стороны оси симметрии параболы
        double x = (x1 + x4) / 2;
        double y = (y1 + y4) / 2;
        double r = sqrt((x1 - x4) * (x1 - x4) + (y1 - y4) * (y1 - y4)) / 2;

        if ((x == org->X() && y == org->Y()) ||
            (x == dest->X() && y == dest->Y()))
          return QPair<QPointF, double>(QPointF(0, 0), -1);

        return (QPair<QPointF, double>(QPointF(x, y), r));
      } else {
        return (QPair<QPointF, double>(QPointF(0, 0), -1));
      }
    } else {
      double x1 = ((TVertex*)Sites[0])->p->X;
      double y1 = ((TVertex*)Sites[0])->p->Y;
      double x2 = ((TVertex*)Sites[1])->p->X;
      double y2 = ((TVertex*)Sites[1])->p->Y;

      double cOrg = (org->X() - x1) * (y2 - y1) - (org->Y() - y1) * (x2 - x1);
      double cDest =
          (dest->X() - x1) * (y2 - y1) - (dest->Y() - y1) * (x2 - x1);
      if (cOrg * cDest < 0) {
        double x = (x1 + x2) / 2;
        double y = (y1 + y2) / 2;
        double r = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)) / 2;
        return (QPair<QPointF, double>(QPointF(x, y), r));
      } else {
        return (QPair<QPointF, double>(QPointF(0, 0), -1));
      }
    }
  }
}

#define xMin org->X()
#define yMin org->Y()
#define rMin org->r()
#define xMax dest->X()
#define yMax dest->Y()
#define rMax dest->r()

void TBone::FillInfo() {
  if (org->r() > dest->r()) {
    TNode* temp = org;
    org = dest;
    dest = temp;
  }

  if (type == BoneType::Linear) {
    double l =
        sqrt((xMax - xMin) * (xMax - xMin) + (yMax - yMin) * (yMax - yMin));
    t = sqrt(max(l * l - (rMax - rMin) * (rMax - rMin), 0.0));
    p = (l > 0) ? acos(min((rMax - rMin) / l, 1.0)) : M_PI_2;
    s = t * (rMin + rMax);
    dx = (xMax - xMin) / l;
    dy = (yMax - yMin) / l;
    if (isnan(s)) throw("Square is not a number");
    return;
  }

  if (type == BoneType::Parabolic) {
    if (!Sites[0]->IsVertex()) {
      // Сайт-точка будет всегда идти первым
      TSite* temp = Sites[0];
      Sites[0] = Sites[1];
      Sites[1] = temp;
    }
    double x1 = ((TVertex*)Sites[0])->p->X;
    double y1 = ((TVertex*)Sites[0])->p->Y;
    double x2 = ((TEdge*)Sites[1])->org->X;
    double y2 = ((TEdge*)Sites[1])->org->Y;
    double x3 = ((TEdge*)Sites[1])->dest->X;
    double y3 = ((TEdge*)Sites[1])->dest->Y;
    double a = ((x1 - x2) * (x3 - x2) + (y1 - y2) * (y3 - y2)) /
               ((x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2));
    // Отношение длины проекции к длине сайта-сегмента
    double x4 = x2 + a * (x3 - x2);
    double y4 = y2 + a * (y3 - y2);
    x0 = (x1 + x4) / 2;
    y0 = (y1 + y4) / 2;
    p = sqrt((x1 - x4) * (x1 - x4) + (y1 - y4) * (y1 - y4));
    t = sqrt(max(2 * p * (rMax - p / 2), 0.0));
    s = (rMax + p) / 2 * t -
        (rMin + p) / 2 * sqrt(2 * p * max(rMin - p / 2, 0.0));
    dx = (y1 - y4) / p;
    dy = -(x1 - x4) / p;
    dir = 1;
    // Направляющий вектор оси OY
    if ((xMax - x0) * dx + (yMax - y0) * dy < 0) {
      // Поворот от OX к OY производится по часовой стрелке
      dx = -dx;
      dy = -dy;
      dir = -1;
    }
    if (isnan(s)) throw("Square is not a number");
    return;
  }

  if (type == BoneType::Hyperbolic) {
    double x1 = ((TVertex*)Sites[0])->p->X;
    double y1 = ((TVertex*)Sites[0])->p->Y;
    double x2 = ((TVertex*)Sites[1])->p->X;
    double y2 = ((TVertex*)Sites[1])->p->Y;
    x0 = (x1 + x2) / 2;
    y0 = (y1 + y2) / 2;
    p = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
    t = sqrt(max(rMax * rMax - p * p / 4, 0.0));
    s = p / 2 * t - p / 2 * sqrt(max(rMin * rMin - p * p / 4, 0.0));
    if (t > 0) {
      dx = (xMax - x0) / t;
      dy = (yMax - y0) / t;
    } else {
      dx = (y1 - y2) / p;
      dy = (x2 - x1) / p;
    }
    if (isnan(s)) throw("Square is not a number");
    return;
  }
}

double TBone::Square(double rad) {
  if (rad <= rMin) {
    return s;
  }
  if (rad > rMax) {
    return 0;
  }

  if (type == BoneType::Linear) {
    double q = (t > 0) ? t * (rMax - rad) / (rMax - rMin) : 0;
    return q * (rad + rMax);
  }
  if (type == BoneType::Parabolic) {
    double q = sqrt(max(2 * p * (rad - p / 2), 0.0));
    return (rMax + p) / 2 * t - (rad + p) / 2 * q;
  }

  // Бицикл - гиперболический
  return p / 2 * (t - sqrt(max(rad * rad - p * p / 4, 0.0)));
}

QPair<QPointF, bool> TBone::GetExtremePoint(double r) {
  if (r <= rMin) {
    return QPair<QPointF, bool>(QPointF(xMin, yMin), true);
  } else if (r > rMax) {
    return QPair<QPointF, bool>(QPointF(0, 0), false);
  }
  double a, x = 0, y = 0;

  switch (type) {
    case BoneType::Linear:
      a = (r - rMin) / (rMax - rMin);
      x = xMin + a * (xMax - xMin);
      y = yMin + a * (yMax - yMin);
      break;
    case BoneType::Parabolic:
      a = sqrt(max(2 * p * (r - p / 2), 0.0));
      x = x0 + a * dx - dir * (r - p / 2) * dy;
      y = y0 + a * dy + dir * (r - p / 2) * dx;
      break;
    case BoneType::Hyperbolic:
      a = sqrt(max(r * r - p * p / 4, 0.0));
      x = x0 + a * dx;
      y = y0 + a * dy;
      break;
  }
  if (isnan(x) || isnan(y)) throw("Coordinate is not a number");
  return QPair<QPointF, bool>(QPointF(x, y), true);
}

double TBone::SectorArea(double rad) {
  double angle = 0;
  switch (type) {
    case BoneType::Linear:
      angle = p;
      break;
    case BoneType::Parabolic:
      angle = asin(min((p - rad) / rad, 1.0));
      angle = (angle + M_PI_2) / 2;
      break;
    case BoneType::Hyperbolic:
      angle = asin(min((p / 2) / rad, 1.0));
      break;
  }
  return angle * rad * rad;
}

Lacuna::Lacuna() : color(rand() % 256, rand() % 256, rand() % 256) {}

void Lacuna::AddBone(TBone* Bone, double rad) {
  Bones.push_back(Bone);
  if (Bone->dest->r() >= rad) {
    for (auto Pair = Truncated.begin(); Pair != Truncated.end(); Pair++) {
      if (PairSquare(Bone, *Pair, rad) > 0)
        Pairs.push_back(QPair<TBone*, TBone*>(Bone, *Pair));
    }
    Truncated.push_back(Bone);
  }
}

void Lacuna::Absorb(Lacuna* Inflow, double rad) {
  if (Inflow != this) {
    for (auto iter = Inflow->Bones.begin(); iter != Inflow->Bones.end();
         iter++) {
      (*iter)->lacuna = this;
    }
    Bones.splice(Bones.end(), Inflow->Bones);

    for (auto Cand = Inflow->Truncated.begin(); Cand != Inflow->Truncated.end();
         Cand++) {
      for (auto Pair = Truncated.begin(); Pair != Truncated.end(); Pair++) {
        if (PairSquare(*Cand, *Pair, rad) > 0)
          Pairs.push_back(QPair<TBone*, TBone*>(*Cand, *Pair));
      }
    }
    Truncated.splice(Truncated.end(), Inflow->Truncated);
    Pairs.splice(Pairs.end(), Inflow->Pairs);
  }
}

double PairSquare(TBone* BoneA, TBone* BoneB, double rad) {
  QPointF Points[2];
  for (int i = 0; i < 2; i++) {
    QPair<QPointF, bool> temp = (i == 0 ? BoneA : BoneB)->GetExtremePoint(rad);
    if (temp.second == false) {
      // Ребро полностью исчезло
      return 0.0;
    }
    Points[i] = temp.first;
  }
  double xc = (Points[0].x() + Points[1].x()) / 2;
  double yc = (Points[0].y() + Points[1].y()) / 2;

  for (int i = 0; i < 2; i++) {
    TBone* iBone = (i == 0 ? BoneA : BoneB);
    double dx = iBone->dest->X() - iBone->org->X();
    double dy = iBone->dest->Y() - iBone->org->Y();
    if (dx == 0 && dy == 0) {
      dx = iBone->dx;
      dy = iBone->dy;
    }

    double ax, ay;
    if (iBone->type == BoneType::Linear) {
      ax = ((TEdge*)iBone->Sites[0])->dest->X -
           ((TEdge*)iBone->Sites[0])->org->X;
      ay = ((TEdge*)iBone->Sites[0])->dest->Y -
           ((TEdge*)iBone->Sites[0])->org->Y;
    } else {
      ax = ((TVertex*)iBone->Sites[0])->p->Y - Points[i].y();
      ay = -(((TVertex*)iBone->Sites[0])->p->X - Points[i].x());
    }
    double b = ax * Points[i].x() + ay * Points[i].y();
    double d0 = ax * dx + ay * dy;
    double d1 = ax * xc + ay * yc - b;
    if (d0 * d1 >= 0) return 0.0;

    if (iBone->type == BoneType::Hyperbolic) {
      ax = ((TVertex*)iBone->Sites[1])->p->Y - Points[i].y();
      ay = -(((TVertex*)iBone->Sites[1])->p->X - Points[i].x());
    } else {
      ax = ((TEdge*)iBone->Sites[1])->dest->X -
           ((TEdge*)iBone->Sites[1])->org->X;
      ay = ((TEdge*)iBone->Sites[1])->dest->Y -
           ((TEdge*)iBone->Sites[1])->org->Y;
    }
    b = ax * Points[i].x() + ay * Points[i].y();
    d0 = ax * dx + ay * dy;
    d1 = ax * xc + ay * yc - b;
    if (d0 * d1 >= 0) return 0.0;
  }

  double l = sqrt(pow(Points[1].x() - Points[0].x(), 2) +
                  pow(Points[1].y() - Points[0].y(), 2));
  if (l > 2 * rad) {
    return 0.0;
  }
  double h = sqrt(rad * rad - l * l / 4);
  double angle = asin(h / rad);
  double s = 2 * (angle * rad * rad - (l / 2) * h);
  if (isnan(s)) throw("Square is not a number");
  return s;
}
