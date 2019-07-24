const plan = Frontrow.plan('Pretix');
plan.size = {width: 1150, height: 1150};
plan.addCategory('Parkett vorne', '#7f4a91')
plan.addCategory('Parkett mitte', '#d36060');
plan.addCategory('Parkett hinten', '#5f9cd4');
plan.addCategory('Balkon vorne', '#7f4a91');
plan.addCategory('Balkon hinten', '#d36060')

const parkett = plan.addZone({
  name: 'Ground floor',
  position: {x: 0, y: 0}
});

const rowshifts = {
  1: 4,
  2: 3,
  3: 2,
  4: 2,
  5: 2,
  6: 1,
  7: 0,
  8: 7,
  9: 7,
  10: 2,
  11: 2,
  12: 2,
  13: 4,
  14: 3,
  15: 7,
  16: 7,
  17: 3,
  18: 3,
  19:3,
  20: 3,
  21:3,
  22:3,
  23:3,
  24:3,
  
};

const rowlengths = {
  1: 26,
  2: 28,
  3: 30,
  4: 30,
  5: 30,
  6: 32,
  7: 34,
  8: 28,
  9: 20,
  10: 25,
  11: 30,
  12: 30,
  13: 26,
  14: 28,
  15: 28,
  16: 28,
  17: 28,
  18: 28,
  19: 28,
  20: 28,
  21: 28,
  22: 28,
  23: 28,
  24: 28
};

parkett.areas = [
  {
    "color": "#eee",
    "shape": "rectangle",
    	"position": {x: 12*30, y: 0},
    "rectangle": {
  		"width": 13*30,
  		"height": 50
  	},
    "text": {
    	"position": {x: 12 * 30/2, y: 26},
  		"text": "STAGE"
  	}
  }
]

for (let rowindex of Array(32).keys()) {
  let rownr = rowindex + 1;
  let row = parkett.addRow({
    row_number: rownr.toString(),
    position: {
      x: 10, y: 25 * rownr + 60
    }
  })
  let seatnr = 1;
  
  for (let seatindex of Array(35).keys()) {
    if (seatindex < rowshifts[rowindex + 1]) {
      continue;
    }
    if (seatnr > rowlengths[rowindex + 1]) {
      continue;
    }
    let xoff = 30 * seatindex;
    if (seatindex > 6) {
      xoff += 30
    }
    if (seatindex > 16) {
      xoff += 30
    }
    if (seatindex > 26) {
      xoff += 30
    }
    let category = 'Parkett vorne';
    if ((seatindex <= 6 || seatindex >= 27) && rownr <= 7) {
      category = 'Parkett vorne';
    }
    if ((seatindex <= 2 || seatindex >= 31) && rownr <= 8) {
      category = 'Parkett mitte';
    }
    if (rownr >= 10) {
      category = 'Parkett mitte';
      if (seatindex <= 6 || seatindex >= 27 || rownr >= 14) {
        category = 'Parkett hinten';
      }
    }
    row.addSeat({
      seat_number: rownr + '-' + seatnr,
      seat_guid: rownr + '-' + seatnr,
      position: {
        x: xoff, y: 0
      },
      category: category
    })
    seatnr++
  }
}

const balkon = plan.addZone({
  name: 'Balcony',
  position: {x: 0, y: 32 * 25 + 120}
});

for (let rowindex of Array(3).keys()) {
  let rownr = rowindex + 17;
  let row = balkon.addRow({
    row_number: rownr.toString(),
    position: {
      x: 10, y: 25 * (rowindex + 1) + 60
    }
  })
  let seatnr = 1;
  
  for (let seatindex of Array(34).keys()) {
    if (rowindex != 1 && seatindex == 33) {
      continue;
    }
    let xoff = 3 * 30 + 30 * seatindex;
    let category = 'Balkon vorne';
    if (rowindex > 0) {
      category = 'Balkon hinten';
    }
    row.addSeat({
      seat_number: rownr + '-' + seatnr,
      seat_guid: rownr + '-' + seatnr,
      position: {
        x: xoff, y: 0
      },
      category: category
    })
    seatnr++
  }
}
balkon.areas = [
  {
    "color": "transparent",
    "shape": "rectangle",
    	"position": {x: 0, y: 0},
    "rectangle": {
  		"width": 1150,
  		"height": 180
  	},
    "text": {
    	"position": {x: 18 * 30 + 10, y: 26},
  		"text": "BALCONY"
  	}
  }
]

plan.getPlan();
