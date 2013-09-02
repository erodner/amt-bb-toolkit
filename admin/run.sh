#!/usr/bin/env sh
#
# Copyright 2008 Amazon Technologies, Inc.
# 
# Licensed under the Amazon Software License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# 
# http://aws.amazon.com/asl
# 
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and
# limitations under the License.

. config.sh

dir=$1
shift
name=$1
shift

if [ -z "$dir" ] || [ -z "$name" ]; then
  echo "usage: ./run.sh <directory-with-configs> <name-of-config>" >&2
  exit 1
fi

label=$dir/$name 
input=$dir/$name.input
question=$dir/$name.question
properties=$dir/$name.properties
echo "run on : $name ($dir)"
cd $MTURK_TOOLS_DIR
./loadHITs.sh -label $label -input $input -question $question -properties $properties $*


