#pragma once

/*Модуль содержит процедуры построения графа смежности сайтов
  многоугольной фигуры в виде обобщённой триангуляции Делоне,
  состоящей из вершин, рёбер и граней.*/

#include <QDebug>
#include <vector>
#include "Geometry.h"
#include "LinkedList.h"
#include "StructureTD.h"
using std::vector;

void ProduceElements(Domain* Collect);
/* Построение элементов триангуляции */
void CreateTriangulation(Domain* Collect);
/* Построение трангуляции и скелета */
