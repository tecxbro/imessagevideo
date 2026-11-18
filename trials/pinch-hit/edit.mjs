export const FPS = 24;
export const width = 1280;
export const height = 720;

const early = {
  end: 576,
  entrance: 20,
  fieldCut: 98,
  requestCut: 160,
  send: 201,
  pending: 237,
  chairReturn: 267,
  confirmationCut: 352,
  confirmed: 370,
  bookCut: 438,
  pencilDown: 466,
  markComplete: 500,
  title: 529,
};

export const edits = {
  early,
  'hold-test': {
    ...early,
    confirmationCut: 340,
    confirmed: 358,
    bookCut: 426,
    pencilDown: 454,
    markComplete: 488,
  },
  alternate: {
    end: 528,
    vibrate: 23,
    askCut: 55,
    accept: 196,
    confirmationCut: 239,
    confirmed: 298,
    bookCut: 366,
    pencilDown: 395,
    markComplete: 429,
    title: 480,
  },
  final: {
    end: 576,
    entrance: 20,
    fieldCut: 78,
    requestCut: 128,
    send: 170,
    pending: 193,
    chairReturn: 230,
    askCut: 274,
    accept: 352,
    occupiedCut: 374,
    confirmed: 392,
    bookCut: 469,
    pencilDown: 488,
    markComplete: 513,
    title: 536,
  },
};
