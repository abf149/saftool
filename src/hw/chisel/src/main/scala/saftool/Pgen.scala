// See README.md for license details.



import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Parallel prefix sum wrapper input interface encapsulation*/
class ParallelPrefixSumWrapperInputBundle(val bitwidth: Int) extends Bundle {
  val bitmask = Input(UInt(bitwidth.W))
}

/* Parallel prefix sum wrapper output interface encapsulation*/
class ParallelPrefixSumWrapperOutputBundle(val bitwidth: Int, val num_items: Int) extends Bundle {
  val sums = Output(Vec(num_items,UInt(bitwidth.W)))
}

/* Combinational Kogge-Stone parallel prefix sum */
class ParallelKoggeStonePrefixSumCombinational(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits,bitwidth))

  // Build one level of Kogge-Stone parallel prefix-sum
  def doBuild(current_level: Array[UInt], num_elements: Int, lvl_idx: Int): Array[UInt] = {
    val lvl_stride = pow(2,lvl_idx).toInt
    val bits_in = lvl_idx+1
    val bits_out = lvl_idx+2
    val new_level = new Array[UInt](num_elements)

    for (jdx <- 0 until lvl_stride) {
      new_level(jdx) = Wire(UInt(bits_out.W))
      new_level(jdx) := current_level(jdx).zext.asUInt
    }

    //println("second loop")
    for (jdx <- lvl_stride until num_elements) {
      //println("j",jdx)      
      new_level(jdx) = Wire(UInt(bits_out.W))
      new_level(jdx) := current_level(jdx).zext.asUInt + current_level(jdx - lvl_stride).zext.asUInt
    }

    return new_level
  }

  val num_lvls = output_wordbits
  var logic_lvls:Array[Array[UInt]] = new Array[Array[UInt]](num_lvls)

  logic_lvls(0) = new Array[UInt](bitwidth)    
  for (kdx <- 0 until bitwidth) {
    logic_lvls(0)(kdx) = Wire(UInt(1.W))
    logic_lvls(0)(kdx) := input.bitmask(kdx)
  }

  // Build successive Kogge-Stone layers
  for (idx <- 1 until num_lvls) {
    logic_lvls(idx) = doBuild(logic_lvls(idx-1), bitwidth, idx-1)
  }

  // Wire Kogge-Stone final layer to output

  for (idx <- 0 until bitwidth) {
    output.sums(idx) := logic_lvls(num_lvls-1)(idx)
  }
}

/* Registered interface wrapped around parallel prefix sum */
class ParallelKoggeStonePrefixSumRegistered(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt+1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits,bitwidth))
  val bitmask_reg = RegInit(0.U)
  val output_wordbits_reg = RegInit((VecInit(Seq.fill(bitwidth)(0.U(output_wordbits.W)))))
    
    //bitwidth,UInt(output_wordbits.W)))) //RegInit(Vec(Seq.fill(bitwidth)(0.U(output_wordbits.W))))

  // Combinational unit
  val combinational_prefix_sum = Module(new ParallelKoggeStonePrefixSumCombinational(bitwidth))

  bitmask_reg := input.bitmask
  combinational_prefix_sum.input.bitmask := bitmask_reg
  output_wordbits_reg := combinational_prefix_sum.output.sums
  output.sums := output_wordbits_reg
}

// Fully combinational Ripple parallel prefix sum
class RippleParallelPrefixSumCombinational(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))

  val partial_sums = Wire(Vec(bitwidth, UInt(output_wordbits.W)))

  partial_sums(0) := input.bitmask(0)
  for (i <- 1 until bitwidth) {
    val adder_width = log2Ceil(i + 1) + 1
    val sum = Wire(UInt(adder_width.W))
    sum := partial_sums(i - 1) +& input.bitmask(i)
    partial_sums(i) := sum.zext.asUInt
  }

  output.sums := partial_sums
}

// Registered interface wrapped around the Ripple parallel prefix sum
class RippleParallelPrefixSumRegistered(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))
  val bitmask_reg = RegInit(0.U(bitwidth.W))
  val output_wordbits_reg = RegInit(VecInit(Seq.fill(bitwidth)(0.U(output_wordbits.W))))

  // Combinational unit
  val combinational_prefix_sum = Module(new RippleParallelPrefixSumCombinational(bitwidth))

  bitmask_reg := input.bitmask
  combinational_prefix_sum.input.bitmask := bitmask_reg
  output_wordbits_reg := combinational_prefix_sum.output.sums
  output.sums := output_wordbits_reg
}

// Brent-Kung parallel prefix sum
class BrentKungParallelPrefixSumCombinational(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth) / log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))

  def doUpSweep(current_level: Array[UInt], num_elements: Int, lvl_idx: Int): Array[UInt] = {
    val new_level = new Array[UInt](num_elements)
    val lvl_stride = pow(2, lvl_idx).toInt

    for (jdx <- 0 until num_elements) {
      new_level(jdx) = Wire(UInt((lvl_idx + 2).W))
      if (jdx % lvl_stride == 0 && jdx + lvl_stride < num_elements) {
        new_level(jdx) := current_level(jdx) + current_level(jdx + lvl_stride)
      } else {
        new_level(jdx) := current_level(jdx)
      }
    }

    return new_level
  }

  def doDownSweep(current_level: Array[UInt], num_elements: Int, lvl_idx: Int): Array[UInt] = {
    val new_level = new Array[UInt](num_elements)
    val lvl_stride = pow(2, lvl_idx).toInt

    for (jdx <- 0 until num_elements) {
      new_level(jdx) = Wire(UInt((output_wordbits).W))
    }

    for (jdx <- 0 until num_elements) {
      //new_level(jdx) = Wire(UInt((output_wordbits).W))
      if (jdx % lvl_stride == 0 && jdx + lvl_stride < num_elements) {
        new_level(jdx) := current_level(jdx + lvl_stride)
        new_level(jdx + lvl_stride) := current_level(jdx) + current_level(jdx + lvl_stride)
      } else if (jdx % lvl_stride != 0) {
        new_level(jdx) := current_level(jdx)
      }
    }

    return new_level
  }

  val num_lvls = output_wordbits - 1
  var up_sweep_levels: Array[Array[UInt]] = new Array[Array[UInt]](num_lvls)
  var down_sweep_levels: Array[Array[UInt]] = new Array[Array[UInt]](num_lvls)

  up_sweep_levels(0) = new Array[UInt](bitwidth)
  for (kdx <- 0 until bitwidth) {
    up_sweep_levels(0)(kdx) = Wire(UInt(1.W))
    up_sweep_levels(0)(kdx) := input.bitmask(kdx)
  }

  for (idx <- 1 until num_lvls) {
    up_sweep_levels(idx) = doUpSweep(up_sweep_levels(idx - 1), bitwidth, idx - 1)
  }

  down_sweep_levels(num_lvls - 1) = Array.fill(bitwidth)(Wire(UInt(output_wordbits.W)))
  down_sweep_levels(num_lvls - 1)(0) := 0.U
  for (idx <- 1 until bitwidth) {
    down_sweep_levels(num_lvls - 1)(idx) := up_sweep_levels(num_lvls - 1)(idx)
  }

  for (idx <- num_lvls - 2 to 0 by -1) {
    down_sweep_levels(idx) = doDownSweep(down_sweep_levels(idx + 1), bitwidth, idx)
  }

  for (idx <- 0 until bitwidth) {
    output.sums(idx) := down_sweep_levels(0)(idx)
  }
}

// Registered interface wrapped around Brent-Kung parallel prefix sum
class BrentKungParallelPrefixSumRegistered(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth) / log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))
  val bitmask_reg = RegInit(0.U(bitwidth.W))
  val output_wordbits_reg = RegInit(VecInit(Seq.fill(bitwidth)(0.U(output_wordbits.W))))

  // Combinational unit
  val combinational_prefix_sum = Module(new BrentKungParallelPrefixSumCombinational(bitwidth))

  bitmask_reg := input.bitmask
  combinational_prefix_sum.input.bitmask := bitmask_reg
  output_wordbits_reg := combinational_prefix_sum.output.sums
  output.sums := output_wordbits_reg
}



/* Parallel priority encoder inter-stage interface encapsulation; idx = stage output index, vld = stage output valid */
class PriorityEncoderBundle(val bitwidth: Int) extends Bundle {
  val idx = Output(UInt(bitwidth.W))
  val vld = Output(UInt(1.W))
}

/* Priority encoder first stage - takes two "0-bit" inputs each with a valid signal, outputs 1-bit index with valid signal */
class ParallelDec2PriorityEncoderBaseCombinational() extends Module   with RequireSyncReset {
  val input0 = IO(new Bundle{val vld = Input(UInt(1.W))})
  val input1 = IO(new Bundle{val vld = Input(UInt(1.W))})
  val output = IO(new PriorityEncoderBundle(1))

  output.vld := (input0.vld.asBool || input1.vld.asBool).asUInt
  output.idx := input1.vld
}

/* Priority encoder intermediate stage - takes two n-bit inputs each with a valid signal, outputs n+1-bit index with valid signl */
class ParallelDec2PriorityEncoderStageCombinational(val bitwidth: Int) extends Module   with RequireSyncReset {
  val input0 = IO(Flipped(new PriorityEncoderBundle(bitwidth)))
  val input1 = IO(Flipped(new PriorityEncoderBundle(bitwidth)))
  val output = IO(new PriorityEncoderBundle(bitwidth+1))

  output.vld := (input0.vld.asBool || input1.vld.asBool).asUInt
  output.idx := Mux(input1.vld.asBool,Cat(input1.vld,input1.idx),Cat(input1.vld,input0.idx))
}

class ParallelDec2PriorityEncoderCombinational(val inputbits: Int) extends Module with RequireSyncReset {
  val output_bits = (log10(inputbits)/log10(2.0)).toInt

  val input = IO(new Bundle{val in = Input(UInt(inputbits.W))})
  val output = IO(new PriorityEncoderBundle(output_bits))
  
  def doBuild(base_offset: Int, cur_inputbits: Int, cur_output: PriorityEncoderBundle): Unit =
    //val new_inputbits = (cur_inputbits/2).toInt 

    

    if (cur_inputbits > 0) {
      val stage_penc = Module(new ParallelDec2PriorityEncoderStageCombinational((cur_inputbits).toInt))
      cur_output.vld := stage_penc.output.vld
      cur_output.idx := stage_penc.output.idx
      doBuild(base_offset, (cur_inputbits-1).toInt, stage_penc.input0)
      doBuild(base_offset+(inputbits/(pow(2,output_bits-cur_inputbits))).toInt, (cur_inputbits-1).toInt, stage_penc.input1)      


    } else {
      val base_penc = Module(new ParallelDec2PriorityEncoderBaseCombinational())
      cur_output.vld := base_penc.output.vld
      cur_output.idx := base_penc.output.idx
      base_penc.input0.vld := input.in(base_offset)
      base_penc.input1.vld := input.in(base_offset+1)
    }

  doBuild(0, output_bits-1, output)
}

/* Registered interface wrapped around combinatorial parallel priority encoder */
class ParallelDec2PriorityEncoderRegistered(val inputbits: Int) extends Module with RequireSyncReset {
  val output_bits = (log10(inputbits)/log10(2.0)).toInt

  val input = IO(new Bundle{val in = Input(UInt(inputbits.W))})
  val output = IO(new PriorityEncoderBundle(output_bits))
  val input_reg = RegInit(0.U)
  val output_idx_reg = RegInit(0.U) 
  val output_vld_reg = RegInit(0.U)

  // Combinational unit (TODO: typo)
  val combinatorial_penc = Module(new ParallelDec2PriorityEncoderCombinational(inputbits))

  input_reg := input.in
  combinatorial_penc.input.in := input_reg
  output_idx_reg := combinatorial_penc.output.idx
  output_vld_reg := combinatorial_penc.output.vld 
  output.idx := output_idx_reg
  output.vld := output_vld_reg
}

