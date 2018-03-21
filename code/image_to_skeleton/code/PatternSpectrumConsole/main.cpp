#include "PatternSpectrum.h"

int main(int argc, char* argv[]) {
  bool ok;

  if (argc < 3) {
    printf("You must specify ignorable area and step\n");
    return -1;
  }

  int area = QString(argv[1]).toInt(&ok);
  if (!ok) {
    printf("Invalid ignorable area value\n");
    return -1;
  } else if (area < 0) {
    printf("Ignorable area value can't be negative\n");
    return -1;
  }

  double step = QString(argv[2]).toDouble(&ok);
  if (!ok) {
    printf("Invalid step area value\n");
    return -1;
  } else if (step <= 0) {
    printf("Step value must be positive\n");
    return -1;
  }

  int class_label = QString(argv[4]).toInt(&ok);
  string output_filename(argv[5]);
  double pruning = QString(argv[6]).toDouble(&ok);

  PatternSpectrum Spectrum(area, step, class_label, output_filename,pruning);

  ifstream file((argc > 3) ? argv[3] : "files.txt");
  char* path = new char[1024];
  while (file.getline(path, 1024)) {
    if (path[0] != '\0') Spectrum.ProcessImage(QString(path));
  }

  return 0;
}
