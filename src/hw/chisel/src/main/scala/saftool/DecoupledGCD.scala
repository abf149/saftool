// See README.md for license details.

package saftool

import chisel3._
import chisel3.util.Decoupled

class GcdInputBundle(val w: Int) extends Bundle {
  val value1 = UInt(w.W)
  val value2 = UInt(w.W)
}

class GcdOutputBundle(val w: Int) extends Bundle {
  val value1 = UInt(w.W)
  val value2 = UInt(w.W)
  val gcd    = UInt(w.W)
}

/**
  * Compute Gcd using subtraction method.
  * Subtracts the smaller from the larger until register y is zero.
  * value input register x is then the Gcd.
  * Unless first input is zero then the Gcd is y.
  * Can handle stalls on the producer or consumer side
  */
class DecoupledGcd(width: Int) extends Module  with RequireSyncReset{
  val input = IO(Flipped(Decoupled(new GcdInputBundle(width))))
  val output = IO(Decoupled(new GcdOutputBundle(width)))

  val xInitial    = Reg(UInt())
  val yInitial    = Reg(UInt())
  val x           = Reg(UInt())
  val y           = Reg(UInt())
  val busy        = RegInit(false.B)
  val resultValid = RegInit(false.B)

  val intersectCombinational = Module(new IntersectFmtCDirBidirCombinational(width))
  intersectCombinational.io.in0 := 0.U
  intersectCombinational.io.in1 := 0.U

  input.ready := ! busy
  output.valid := resultValid
  output.bits := DontCare

  when(busy)  {
    when(x > y) {
      x := x - y
    }.otherwise {
      y := y - x
    }
    when(x === 0.U || y === 0.U) {
      when(x === 0.U) {
        output.bits.gcd := y
      }.otherwise {
        output.bits.gcd := x
      }

      output.bits.value1 := xInitial
      output.bits.value2 := yInitial
      resultValid := true.B

      when(output.ready && resultValid) {
        busy := false.B
        resultValid := false.B
      }
    }
  }.otherwise {
    when(input.valid) {
      val bundle = input.deq()
      x := bundle.value1
      y := bundle.value2
      xInitial := bundle.value1
      yInitial := bundle.value2
      busy := true.B
    }
  }
}

/**
  * Compute Gcd using subtraction method.
  * Subtracts the smaller from the larger until register y is zero.
  * value input register x is then the Gcd.
  * Unless first input is zero then the Gcd is y.
  * Can handle stalls on the producer or consumer side
  */
class DecoupledGcdB(width: Int) extends Module  with RequireSyncReset{
  val input = IO(Flipped(Decoupled(new GcdInputBundle(width))))
  val output = IO(Decoupled(new GcdOutputBundle(width)))

  val xInitial    = Reg(UInt())
  val yInitial    = Reg(UInt())
  val x           = Reg(UInt())
  val y           = Reg(UInt())
  val busy        = RegInit(false.B)
  val resultValid = RegInit(false.B)

  input.ready := ! busy
  output.valid := resultValid
  output.bits := DontCare

  when(busy)  {
    when(x > y) {
      x := x - y
    }.otherwise {
      y := y - x
    }
    when(x === 0.U || y === 0.U) {
      when(x === 0.U) {
        output.bits.gcd := y
      }.otherwise {
        output.bits.gcd := x
      }

      output.bits.value1 := xInitial
      output.bits.value2 := yInitial
      resultValid := true.B

      when(output.ready && resultValid) {
        busy := false.B
        resultValid := false.B
      }
    }
  }.otherwise {
    when(input.valid) {
      val bundle = input.deq()
      x := bundle.value1
      y := bundle.value2
      xInitial := bundle.value1
      yInitial := bundle.value2
      busy := true.B
    }
  }
}

/*
// Intersect unit {Format: C, metadata orchestration: uncoupled}
class AUX_Intersect_Format_C_MDOrch_Uncoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {
  //val clock = IO(Input(Clock()))
  //val reset = IO(Input(Reset()))
  val io = IO(new Bundle {
    val in0 = Input(UInt(metaDataWidth.W))
    val in1 = Input(UInt(metaDataWidth.W))
    val out_intersect = Output(UInt(metaDataWidth.W))
    val out_in1_geq_in0 = Output(UInt())
    val out_in1_eq_in0 = Output(UInt())
  })

  val out_intersect_reg =   RegInit(0.U)
  val out_in1_geq_in0_reg = RegInit(0.U)
  val out_in1_eq_in0_reg = RegInit(0.U)
  
  out_intersect_reg := io.in0
  out_in1_geq_in0_reg := (io.in1 >= io.in0)
  out_in1_eq_in0_reg := (io.in1 === io.in0)   

  io.out_intersect := out_intersect_reg
  io.out_in1_geq_in0 := out_in1_geq_in0_reg
  io.out_in1_eq_in0 := out_in1_eq_in0_reg  
}
*/